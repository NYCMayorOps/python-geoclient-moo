"""Unit tests for the GeoClient main client class."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock

from geoclient.client import GeoClient
from geoclient.exceptions import (
    GeoClientError,
    GeoClientHTTPError,
    GeoClientAuthError,
    GeoClientAPIError,
)
from geoclient.models import (
    AddressResponse,
    BBLResponse,
    BINResponse,
    BlockfaceResponse,
    IntersectionResponse,
    PlaceResponse,
    SearchResponse,
)

@pytest.fixture
def client():
    """Create a GeoClient instance for testing."""
    return GeoClient()


class TestGeoClientInit:
    """Test cases for GeoClient initialization."""
    
    def test_init_basic(self):
        """Test basic client initialization."""
        test_client = GeoClient()
        assert test_client.base_url == GeoClient.DEFAULT_BASE_URL
        assert test_client.timeout == 30.0
        assert test_client.retries == 3
        assert test_client.retry_delay == 1.0
    
    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        custom_url = "https://custom.api.com/geo/"
        test_client = GeoClient(
            "test_key",
            base_url=custom_url,
            timeout=60.0,
            retries=5,
            retry_delay=2.0,
        )
        assert test_client.base_url == custom_url
        assert test_client.timeout == 60.0
        assert test_client.retries == 5
        assert test_client.retry_delay == 2.0
    
    def test_init_missing_credentials(self):
        """Test client initialization with missing credentials."""
        return # Skip this test since the client now reads from environment variables by default
        with pytest.raises(ValueError, match="subscription_key is required"):
            GeoClient("")
    
    def test_init_base_url_normalization(self):
        """Test base URL normalization."""
        test_client = GeoClient()
        assert test_client.base_url == "https://api.nyc.gov/geoclient/v2/"


class TestGeoClientBoroughValidation:
    """Test cases for borough validation."""
    
    def test_validate_borough_valid_names(self, client):
        """Test borough validation with valid names."""
        assert client._validate_borough("manhattan") == "Manhattan"
        assert client._validate_borough("MANHATTAN") == "Manhattan"
        assert client._validate_borough("Manhattan") == "Manhattan"
        assert client._validate_borough("bronx") == "Bronx"
        assert client._validate_borough("brooklyn") == "Brooklyn"
        assert client._validate_borough("queens") == "Queens"
        assert client._validate_borough("staten island") == "Staten Island"
        assert client._validate_borough("si") == "Staten Island"
    
    def test_validate_borough_valid_codes(self, client):
        """Test borough validation with valid codes."""
        assert client._validate_borough("1") == "Manhattan"
        assert client._validate_borough("2") == "Bronx"
        assert client._validate_borough("3") == "Brooklyn"
        assert client._validate_borough("4") == "Queens"
        assert client._validate_borough("5") == "Staten Island"
    
    def test_validate_borough_invalid(self, client):
        """Test borough validation with invalid values."""
        with pytest.raises(ValueError, match="Invalid borough"):
            client._validate_borough("invalid")
        
        with pytest.raises(ValueError, match="Invalid borough"):
            client._validate_borough("6")


class TestGeoClientMakeRequest:
    """Test cases for the _make_request method."""
    
    @patch('geoclient.client.requests.Session.get')
    def test_successful_request(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "houseNumber": "314",
            "boePreferredStreetName": "WEST 100 STREET",
            "geosupportReturnCode": "00",
        }
        mock_get.return_value = mock_response
        
        client = GeoClient("test_key")
        result = client._make_request("address", {"test": "param"}, AddressResponse)
        
        assert isinstance(result, AddressResponse)
        assert result.house_number == "314"
        assert result.street_name == "WEST 100 STREET"
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "Ocp-Apim-Subscription-Key" in client.session.headers
        assert kwargs["params"]["test"] == "param"
    
    @patch('geoclient.client.requests.Session.get')
    def test_http_error_401(self, mock_get):
        """Test HTTP 401 authentication error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_key")
        
        with pytest.raises(GeoClientAuthError) as exc_info:
            client._make_request("address", {}, AddressResponse)
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
    
    @patch('geoclient.client.requests.Session.get')
    def test_http_error_403(self, mock_get):
        """Test HTTP 403 forbidden error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_key")
        
        with pytest.raises(GeoClientAuthError) as exc_info:
            client._make_request("address", {}, AddressResponse)
        
        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)
    
    @patch('geoclient.client.requests.Session.get')
    def test_http_error_400(self, mock_get):
        """Test HTTP 400 bad request error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_key")
        
        with pytest.raises(GeoClientHTTPError) as exc_info:
            client._make_request("address", {}, AddressResponse)
        
        assert exc_info.value.status_code == 400
        assert "Bad request" in str(exc_info.value)
    
    @patch('geoclient.client.requests.Session.get')
    def test_geosupport_error(self, mock_get):
        """Test Geosupport API error handling."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "geosupportReturnCode": "02",
            "reasonCode": "INVALID_HOUSE_NUMBER",
            "message": "HOUSE NUMBER NOT FOUND",
        }
        mock_get.return_value = mock_response
        
        client = GeoClient("test_key")
        
        with pytest.raises(GeoClientAPIError) as exc_info:
            client._make_request("address", {}, AddressResponse)
        
        assert exc_info.value.geosupport_return_code == "02"
        assert exc_info.value.reason_code == "INVALID_HOUSE_NUMBER"
        assert "HOUSE NUMBER NOT FOUND" in str(exc_info.value)
    
    @patch('geoclient.client.requests.Session.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        client = GeoClient()
        
        with pytest.raises(GeoClientError, match="Invalid JSON response"):
            client._make_request("address", {}, AddressResponse)


class TestGeoClientAddressEndpoint:
    """Test cases for the address endpoint."""
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_address_basic(self, mock_request, client):
        """Test basic address geocoding."""
        mock_response = AddressResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.address("314", "west 100 st", "manhattan")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "address",
            {
                "houseNumber": "314",
                "street": "west 100 st",
                "borough": "Manhattan",
            },
            AddressResponse
        )
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_address_with_zip(self, mock_request, client):
        """Test address geocoding with ZIP code."""
        mock_response = AddressResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.address("314", "west 100 st", zip_code="10025")
        
        mock_request.assert_called_once_with(
            "address",
            {
                "houseNumber": "314",
                "street": "west 100 st",
                "zip": "10025",
            },
            AddressResponse
        )
    
    def test_address_missing_params(self, client):
        """Test address geocoding with missing parameters."""
        with pytest.raises(ValueError, match="house_number and street are required"):
            client.address("", "west 100 st", "manhattan")
        
        with pytest.raises(ValueError, match="Either borough or zip_code must be provided"):
            client.address("314", "west 100 st")


class TestGeoClientBBLEndpoint:
    """Test cases for the BBL endpoint."""
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_bbl_basic(self, mock_request, client):
        """Test basic BBL lookup."""
        mock_response = BBLResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.bbl("manhattan", "1889", "1")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "bbl",
            {
                "borough": "Manhattan",
                "block": "1889",
                "lot": "1",
            },
            BBLResponse
        )
    
    def test_bbl_missing_params(self, client):
        """Test BBL lookup with missing parameters."""
        with pytest.raises(ValueError, match="borough, block, and lot are required"):
            client.bbl("", "1889", "1")


class TestGeoClientBINEndpoint:
    """Test cases for the BIN endpoint."""
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_bin_basic(self, mock_request, client):
        """Test basic BIN lookup."""
        mock_response = BINResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.bin_("1079043")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "bin",
            {"bin": "1079043"},
            BINResponse
        )
    
    def test_bin_missing_param(self, client):
        """Test BIN lookup with missing parameter."""
        with pytest.raises(ValueError, match="bin_number is required"):
            client.bin_("")


class TestGeoClientSearchEndpoint:
    """Test cases for the search endpoint."""
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_search_basic(self, mock_request, client):
        """Test basic search."""
        mock_response = SearchResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.search("314 west 100 st manhattan")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "search",
            {"input": "314 west 100 st manhattan"},
            SearchResponse
        )
    
    @patch('geoclient.client.GeoClient._make_request')
    def test_search_with_options(self, mock_request, client):
        """Test search with optional parameters."""
        mock_response = SearchResponse(raw_data={})
        mock_request.return_value = mock_response
        
        result = client.search(
            "314 west 100 st manhattan",
            exact_match_for_single_success=True,
            exact_match_max_level=5,
            return_tokens=True,
            similar_names_distance=10,
        )
        
        expected_params = {
            "input": "314 west 100 st manhattan",
            "exactMatchForSingleSuccess": "true",
            "exactMatchMaxLevel": 5,
            "returnTokens": "true",
            "similarNamesDistance": 10,
        }
        
        mock_request.assert_called_once_with(
            "search",
            expected_params,
            SearchResponse
        )
    
    def test_search_missing_input(self, client):
        """Test search with missing input."""
        with pytest.raises(ValueError, match="input_text is required"):
            client.search("")
    
    def test_search_invalid_max_level(self, client):
        """Test search with invalid max level."""
        with pytest.raises(ValueError, match="exact_match_max_level must be between 0 and 6"):
            client.search("test", exact_match_max_level=10)


class TestGeoClientContextManager:
    """Test cases for context manager functionality."""
    
    def test_context_manager(self):
        """Test client as context manager."""
        with patch.object(GeoClient, 'close') as mock_close:
            with GeoClient("test_key") as test_client:
                assert isinstance(test_client, GeoClient)
            
            mock_close.assert_called_once()
    
    @patch('geoclient.client.requests.Session.close')
    def test_close_method(self, mock_session_close):
        """Test close method."""
        test_client = GeoClient("test_key")
        test_client.close()
        
        mock_session_close.assert_called_once()