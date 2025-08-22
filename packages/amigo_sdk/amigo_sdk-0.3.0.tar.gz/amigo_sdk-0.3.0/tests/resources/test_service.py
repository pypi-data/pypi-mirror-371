import pytest

from amigo_sdk.config import AmigoConfig
from amigo_sdk.errors import NotFoundError
from amigo_sdk.generated.model import ServiceGetServicesResponse
from amigo_sdk.http_client import AmigoHttpClient
from amigo_sdk.resources.service import ServiceResource

from .helpers import create_services_response_data, mock_http_request


@pytest.fixture
def mock_config():
    return AmigoConfig(
        api_key="test-api-key",
        api_key_id="test-api-key-id",
        user_id="test-user-id",
        organization_id="test-org-123",
        base_url="https://api.example.com",
    )


@pytest.fixture
def service_resource(mock_config):
    http_client = AmigoHttpClient(mock_config)
    return ServiceResource(http_client, "test-org-123")


@pytest.mark.unit
class TestServiceResource:
    """Simple test suite for ServiceResource."""

    @pytest.mark.asyncio
    async def test_get_services_returns_expected_data(self, service_resource):
        """Test get_services method returns properly parsed services data."""
        mock_data = create_services_response_data()

        async with mock_http_request(mock_data):
            result = await service_resource.get_services()

            assert isinstance(result, ServiceGetServicesResponse)
            assert len(result.services) == 2
            assert result.services[0].id == "service-1"
            assert result.services[0].name == "Customer Support Bot"
            assert result.services[1].id == "service-2"
            assert not result.has_more
            assert result.continuation_token is None

    @pytest.mark.asyncio
    async def test_get_services_nonexistent_organization_raises_not_found(
        self, service_resource
    ):
        """Test get_services method raises NotFoundError for non-existent organization."""
        async with mock_http_request(
            '{"error": "Organization not found"}', status_code=404
        ):
            with pytest.raises(NotFoundError):
                await service_resource.get_services()
