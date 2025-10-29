"""Unit tests for the GeoClient main client class."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock

from geoclient_moo.client import GeoClient
from geoclient_moo.exceptions import (
    GeoClientError,
    GeoClientHTTPError,
    GeoClientAuthError,
    GeoClientAPIError,
)
from geoclient_moo.models import (
    AddressResponse,
    BBLResponse,
    BINResponse,
    BlockfaceResponse,
    IntersectionResponse,
    PlaceResponse,
    SearchResponse,
)


class TestGeoClientInit:
    """Test cases for GeoClient initialization."""
    
    def test_init_basic(self):
        """Test basic client initialization."""
        client = GeoClient("test_id", "test_key")
        assert client.app_id == "test_id"
        assert client.app_key == "test_key"
        assert client.base_url == GeoClient.DEFAULT_BASE_URL
        assert client.timeout == 30.0
        assert client.retries == 3
        assert client.retry_delay == 1.0
    
    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        custom_url = "https://custom.api.com/geo/"
        client = GeoClient(
            "test_id", 
            "test_key",
            base_url=custom_url,
            timeout=60.0,
            retries=5,
            retry_delay=2.0,
        )
        assert client.base_url == custom_url
        assert client.timeout == 60.0
        assert client.retries == 5
        assert client.retry_delay == 2.0
    
    def test_init_missing_credentials(self):
        """Test client initialization with missing credentials."""
        with pytest.raises(ValueError, match="Both app_id and app_key are required"):
            GeoClient("", "test_key")
        
        with pytest.raises(ValueError, match="Both app_id and app_key are required"):
            GeoClient("test_id", "")
    
    def test_init_base_url_normalization(self):
        """Test base URL normalization."""
        client = GeoClient("test_id", "test_key", base_url="https://api.nyc.gov/geo/geoclient/v2")
        assert client.base_url == "https://api.nyc.gov/geo/geoclient/v2/"


class TestGeoClientBoroughValidation:
    """Test cases for borough validation."""
    
    def test_validate_borough_valid_names(self):
        """Test borough validation with valid names."""
        client = GeoClient("test_id", "test_key")
        
        assert client._validate_borough("manhattan") == "Manhattan"
        assert client._validate_borough("MANHATTAN") == "Manhattan"
        assert client._validate_borough("Manhattan") == "Manhattan"
        assert client._validate_borough("bronx") == "Bronx"
        assert client._validate_borough("brooklyn") == "Brooklyn"
        assert client._validate_borough("queens") == "Queens"
        assert client._validate_borough("staten island") == "Staten Island"
        assert client._validate_borough("si") == "Staten Island"
    
    def test_validate_borough_valid_codes(self):
        """Test borough validation with valid codes."""
        client = GeoClient("test_id", "test_key")
        
        assert client._validate_borough("1") == "Manhattan"
        assert client._validate_borough("2") == "Bronx"
        assert client._validate_borough("3") == "Brooklyn"
        assert client._validate_borough("4") == "Queens"
        assert client._validate_borough("5") == "Staten Island"
    
    def test_validate_borough_invalid(self):
        """Test borough validation with invalid values."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="Invalid borough"):
            client._validate_borough("invalid")
        
        with pytest.raises(ValueError, match="Invalid borough"):
            client._validate_borough("6")


class TestGeoClientMakeRequest:
    """Test cases for the _make_request method."""
    
    @patch('geoclient_moo.client.requests.Session.get')
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
        
        client = GeoClient("test_id", "test_key")
        result = client._make_request("address.json", {"test": "param"}, AddressResponse)
        
        assert isinstance(result, AddressResponse)
        assert result.house_number == "314"
        assert result.street_name == "WEST 100 STREET"
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "app_id" in kwargs["params"]
        assert "app_key" in kwargs["params"]
        assert kwargs["params"]["test"] == "param"
    
    @patch('geoclient_moo.client.requests.Session.get')
    def test_http_error_401(self, mock_get):
        """Test HTTP 401 authentication error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(GeoClientAuthError) as exc_info:
            client._make_request("address.json", {}, AddressResponse)
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
    
    @patch('geoclient_moo.client.requests.Session.get')
    def test_http_error_403(self, mock_get):
        """Test HTTP 403 forbidden error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(GeoClientAuthError) as exc_info:
            client._make_request("address.json", {}, AddressResponse)
        
        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)
    
    @patch('geoclient_moo.client.requests.Session.get')
    def test_http_error_400(self, mock_get):
        """Test HTTP 400 bad request error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(GeoClientHTTPError) as exc_info:
            client._make_request("address.json", {}, AddressResponse)
        
        assert exc_info.value.status_code == 400
        assert "Bad request" in str(exc_info.value)
    
    @patch('geoclient_moo.client.requests.Session.get')
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
        
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(GeoClientAPIError) as exc_info:
            client._make_request("address.json", {}, AddressResponse)
        
        assert exc_info.value.geosupport_return_code == "02"
        assert exc_info.value.reason_code == "INVALID_HOUSE_NUMBER"
        assert "HOUSE NUMBER NOT FOUND" in str(exc_info.value)
    
    @patch('geoclient_moo.client.requests.Session.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(GeoClientError, match="Invalid JSON response"):
            client._make_request("address.json", {}, AddressResponse)


class TestGeoClientAddressEndpoint:
    """Test cases for the address endpoint."""
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_address_basic(self, mock_request):
        """Test basic address geocoding."""
        mock_response = AddressResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        result = client.address("314", "west 100 st", "manhattan")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "address.json",
            {
                "houseNumber": "314",
                "street": "west 100 st",
                "borough": "Manhattan",
            },
            AddressResponse
        )
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_address_with_zip(self, mock_request):
        """Test address geocoding with ZIP code."""
        mock_response = AddressResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        result = client.address("314", "west 100 st", zip_code="10025")
        
        mock_request.assert_called_once_with(
            "address.json",
            {
                "houseNumber": "314",
                "street": "west 100 st",
                "zip": "10025",
            },
            AddressResponse
        )
    
    def test_address_missing_params(self):
        """Test address geocoding with missing parameters."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="house_number and street are required"):
            client.address("", "west 100 st", "manhattan")
        
        with pytest.raises(ValueError, match="Either borough or zip_code must be provided"):
            client.address("314", "west 100 st")


class TestGeoClientBBLEndpoint:
    """Test cases for the BBL endpoint."""
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_bbl_basic(self, mock_request):
        """Test basic BBL lookup."""
        mock_response = BBLResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        result = client.bbl("manhattan", "1889", "1")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "bbl.json",
            {
                "borough": "Manhattan",
                "block": "1889",
                "lot": "1",
            },
            BBLResponse
        )
    
    def test_bbl_missing_params(self):
        """Test BBL lookup with missing parameters."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="borough, block, and lot are required"):
            client.bbl("", "1889", "1")


class TestGeoClientBINEndpoint:
    """Test cases for the BIN endpoint."""
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_bin_basic(self, mock_request):
        """Test basic BIN lookup."""
        mock_response = BINResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        result = client.bin_("1079043")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "bin.json",
            {"bin": "1079043"},
            BINResponse
        )
    
    def test_bin_missing_param(self):
        """Test BIN lookup with missing parameter."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="bin_number is required"):
            client.bin_("")


class TestGeoClientSearchEndpoint:
    """Test cases for the search endpoint."""
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_search_basic(self, mock_request):
        """Test basic search."""
        mock_response = SearchResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
        result = client.search("314 west 100 st manhattan")
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            "search.json",
            {"input": "314 west 100 st manhattan"},
            SearchResponse
        )
    
    @patch('geoclient_moo.client.GeoClient._make_request')
    def test_search_with_options(self, mock_request):
        """Test search with optional parameters."""
        mock_response = SearchResponse(raw_data={})
        mock_request.return_value = mock_response
        
        client = GeoClient("test_id", "test_key")
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
            "search.json",
            expected_params,
            SearchResponse
        )
    
    def test_search_missing_input(self):
        """Test search with missing input."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="input_text is required"):
            client.search("")
    
    def test_search_invalid_max_level(self):
        """Test search with invalid max level."""
        client = GeoClient("test_id", "test_key")
        
        with pytest.raises(ValueError, match="exact_match_max_level must be between 0 and 6"):
            client.search("test", exact_match_max_level=10)


class TestGeoClientContextManager:
    """Test cases for context manager functionality."""
    
    def test_context_manager(self):
        """Test client as context manager."""
        with patch.object(GeoClient, 'close') as mock_close:
            with GeoClient("test_id", "test_key") as client:
                assert isinstance(client, GeoClient)
            
            mock_close.assert_called_once()
    
    @patch('geoclient_moo.client.requests.Session.close')
    def test_close_method(self, mock_session_close):
        """Test close method."""
        client = GeoClient("test_id", "test_key")
        client.close()
        
        mock_session_close.assert_called_once()