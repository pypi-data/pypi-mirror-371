from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from amigo_sdk.http_client import AmigoHttpClient
from tests.resources.helpers import (
    mock_http_stream,
    mock_http_stream_sequence,
)


@pytest.fixture
def mock_config():
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="test-org-id",
        base_url="https://api.example.com",
    )


@pytest.fixture
def mock_token_response():
    return Mock(
        id_token="test-bearer-token",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


@pytest.mark.unit
class TestAmigoHttpClient:
    """Test suite for AmigoHttpClient."""

    def test_client_initialization(self, mock_config):
        """Test client initializes correctly with config."""
        client = AmigoHttpClient(mock_config, timeout=30)
        assert client._cfg == mock_config
        assert client._token is None
        assert client._client.base_url == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_ensure_token_fetches_new_token(
        self, mock_config, mock_token_response
    ):
        """Test _ensure_token fetches new token when none exists."""
        client = AmigoHttpClient(mock_config)

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key",
            return_value=mock_token_response,
        ):
            token = await client._ensure_token()

        assert token == "test-bearer-token"
        assert client._token == mock_token_response

    @pytest.mark.asyncio
    async def test_ensure_token_refreshes_expired_token(self, mock_config):
        """Test _ensure_token refreshes token when expired."""
        client = AmigoHttpClient(mock_config)

        # Set an expired token (timezone-aware)
        expired_token = Mock(
            id_token="expired-token",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),  # Expired
        )
        client._token = expired_token

        fresh_token = Mock(
            id_token="fresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
        ):
            token = await client._ensure_token()

        assert token == "fresh-token"
        assert client._token == fresh_token

    @pytest.mark.asyncio
    async def test_ensure_token_handles_auth_failure(self, mock_config):
        """Test _ensure_token raises AuthenticationError when auth fails."""
        client = AmigoHttpClient(mock_config)

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key",
            side_effect=Exception("Auth failed"),
        ):
            with pytest.raises(AuthenticationError):
                await client._ensure_token()

    @pytest.mark.asyncio
    async def test_request_adds_authorization_header(self, mock_config, httpx_mock):
        """Test request method adds Authorization header."""
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/test", status_code=200
        )

        client = AmigoHttpClient(mock_config)

        # Mock token that won't expire
        fresh_token = Mock(
            id_token="test-bearer-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
        ):
            await client.request("GET", "/test")

        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Bearer test-bearer-token"

    @pytest.mark.asyncio
    async def test_request_retries_on_401(self, mock_config, httpx_mock):
        """Test request retries once on 401 response."""
        # First request returns 401, second succeeds
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/test", status_code=401
        )
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/test",
            status_code=200,
            json={"success": True},
        )

        client = AmigoHttpClient(mock_config)

        fresh_token = Mock(
            id_token="fresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
        ):
            response = await client.request("GET", "/test")

        assert response.status_code == 200
        # After 401, token should be refreshed (not None, but fresh)
        assert client._token.id_token == "fresh-token"

    @pytest.mark.asyncio
    async def test_request_raises_error_for_non_2xx(self, mock_config, httpx_mock):
        """Test request raises error for non-2xx responses."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/test",
            status_code=400,
            text="Bad Request",
        )

        client = AmigoHttpClient(mock_config)

        fresh_token = Mock(
            id_token="test-bearer-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
        ):
            with pytest.raises(BadRequestError):
                await client.request("GET", "/test")

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_config):
        """Test client works as async context manager."""
        async with AmigoHttpClient(mock_config) as client:
            assert isinstance(client, AmigoHttpClient)

        # Client should be closed after context exit
        assert client._client.is_closed

    @pytest.mark.asyncio
    async def test_stream_lines_yields_and_sets_headers(self, mock_config):
        client = AmigoHttpClient(mock_config)

        async with mock_http_stream(
            [" line1 ", "", "line2\n", " "], status_code=200
        ) as tracker:
            lines = []
            async for ln in client.stream_lines("GET", "/stream-test"):
                lines.append(ln)

        assert lines == ["line1", "line2"]
        headers = tracker["last_call"]["headers"]
        assert headers["Authorization"] == "Bearer test-bearer-token"
        assert headers["Accept"] == "application/x-ndjson"

    @pytest.mark.asyncio
    async def test_stream_lines_retries_once_on_401(self, mock_config):
        client = AmigoHttpClient(mock_config)

        async with mock_http_stream_sequence([(401, []), (200, ["ok"])]) as tracker:
            lines = []
            async for ln in client.stream_lines("GET", "/retry-401"):
                lines.append(ln)

        assert tracker["call_count"] == 2
        assert lines == ["ok"]

    @pytest.mark.asyncio
    async def test_stream_lines_raises_on_non_2xx(self, mock_config):
        client = AmigoHttpClient(mock_config)

        async with mock_http_stream([], status_code=404):
            with pytest.raises(NotFoundError):
                async for _ in client.stream_lines("GET", "/not-found"):
                    pass

    @pytest.mark.asyncio
    async def test_request_retries_on_408_get(self, mock_config, httpx_mock):
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/r408", status_code=408
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/r408", status_code=200
        )

        client = AmigoHttpClient(mock_config, retry_max_attempts=3)

        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("GET", "/r408")

        assert resp.status_code == 200
        assert len(sleeps) == 1

    @pytest.mark.asyncio
    async def test_request_retries_on_5xx_get(self, mock_config, httpx_mock):
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/r500", status_code=500
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/r500", status_code=200
        )

        client = AmigoHttpClient(mock_config, retry_max_attempts=3)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("GET", "/r500")

        assert resp.status_code == 200
        assert len(sleeps) == 1

    @pytest.mark.asyncio
    async def test_request_retries_on_429_get_respects_retry_after_seconds(
        self, mock_config, httpx_mock
    ):
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/r429s",
            status_code=429,
            headers={"Retry-After": "1.5"},
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/r429s", status_code=200
        )

        client = AmigoHttpClient(
            mock_config,
            retry_max_attempts=3,
            retry_max_delay_seconds=10.0,
        )
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("GET", "/r429s")

        assert resp.status_code == 200
        assert len(sleeps) == 1
        assert sleeps[0] == pytest.approx(1.5, rel=1e-3)

    @pytest.mark.asyncio
    async def test_request_retries_on_429_post_with_retry_after_seconds(
        self, mock_config, httpx_mock
    ):
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/r429p",
            status_code=429,
            headers={"Retry-After": "0.5"},
        )
        httpx_mock.add_response(
            method="POST", url="https://api.example.com/r429p", status_code=200
        )

        client = AmigoHttpClient(mock_config, retry_max_attempts=3)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("POST", "/r429p")

        assert resp.status_code == 200
        assert len(sleeps) == 1
        assert sleeps[0] == pytest.approx(0.5, rel=1e-3)

    @pytest.mark.asyncio
    async def test_request_retries_on_429_post_with_retry_after_http_date(
        self, mock_config, httpx_mock
    ):
        future_dt = datetime.now(timezone.utc) + timedelta(seconds=3)
        http_date = format_datetime(future_dt)

        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/r429pdate",
            status_code=429,
            headers={"Retry-After": http_date},
        )
        httpx_mock.add_response(
            method="POST", url="https://api.example.com/r429pdate", status_code=200
        )

        client = AmigoHttpClient(
            mock_config, retry_max_attempts=3, retry_max_delay_seconds=30.0
        )
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("POST", "/r429pdate")

        assert resp.status_code == 200
        assert len(sleeps) == 1
        # Expect approximately 3 seconds (allow timing variance)
        assert sleeps[0] == pytest.approx(3.0, abs=1.0)

    @pytest.mark.asyncio
    async def test_request_does_not_retry_post_429_without_retry_after(
        self, mock_config, httpx_mock
    ):
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/r429pnora",
            status_code=429,
        )

        client = AmigoHttpClient(mock_config)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            with pytest.raises(RateLimitError):
                await client.request("POST", "/r429pnora")

        assert sleeps == []

    @pytest.mark.asyncio
    async def test_request_retries_on_timeout_get(self, mock_config, httpx_mock):
        httpx_mock.add_exception(
            method="GET",
            url="https://api.example.com/timeout",
            exception=httpx.ReadTimeout("boom"),
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/timeout", status_code=200
        )

        client = AmigoHttpClient(mock_config)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            resp = await client.request("GET", "/timeout")

        assert resp.status_code == 200
        assert len(sleeps) == 1

    @pytest.mark.asyncio
    async def test_request_does_not_retry_post_on_timeout_by_default(
        self, mock_config, httpx_mock
    ):
        httpx_mock.add_exception(
            method="POST",
            url="https://api.example.com/timeout-post",
            exception=httpx.ReadTimeout("boom"),
        )

        client = AmigoHttpClient(mock_config)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        with patch(
            "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
        ):
            with pytest.raises(httpx.TimeoutException):
                await client.request("POST", "/timeout-post")

    @pytest.mark.asyncio
    async def test_backoff_clamps_to_max_delay(self, mock_config, httpx_mock):
        # 500 triggers retry with no Retry-After; cap should apply
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/clamp", status_code=500
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/clamp", status_code=200
        )

        # Make base large so window > cap; force uniform to pick window
        client = AmigoHttpClient(
            mock_config, retry_backoff_base=100.0, retry_max_delay_seconds=0.5
        )
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
            patch("random.uniform", side_effect=lambda a, b: b),
        ):
            resp = await client.request("GET", "/clamp")

        assert resp.status_code == 200
        assert len(sleeps) == 1
        assert sleeps[0] == 0.5

    @pytest.mark.asyncio
    async def test_max_attempts_limits_retries(self, mock_config, httpx_mock):
        # 3 attempts -> 2 sleeps then final failure
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/max", status_code=500
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/max", status_code=500
        )
        httpx_mock.add_response(
            method="GET", url="https://api.example.com/max", status_code=500
        )

        client = AmigoHttpClient(mock_config, retry_max_attempts=3)
        fresh_token = Mock(
            id_token="tok", expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float):
            sleeps.append(seconds)

        with (
            patch(
                "amigo_sdk.http_client.sign_in_with_api_key", return_value=fresh_token
            ),
            patch("asyncio.sleep", new=fake_sleep),
        ):
            with pytest.raises(ServerError):
                await client.request("GET", "/max")

        # 2 sleeps for 3 attempts
        assert len(sleeps) == 2
