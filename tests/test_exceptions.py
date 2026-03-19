"""Unit tests for the GeoClient exceptions."""

import pytest
from geoclient.exceptions import (
    GeoClientError,
    GeoClientHTTPError,
    GeoClientAuthError,
    GeoClientAPIError,
)


class TestGeoClientError:
    """Test cases for GeoClientError base exception."""
    
    def test_basic_error(self):
        """Test basic error creation."""
        error = GeoClientError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}
    
    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"param": "value", "code": 123}
        error = GeoClientError("Test error", details)
        assert error.message == "Test error"
        assert error.details == details


class TestGeoClientHTTPError:
    """Test cases for GeoClientHTTPError."""
    
    def test_http_error_basic(self):
        """Test basic HTTP error."""
        error = GeoClientHTTPError("HTTP error", 500)
        assert str(error) == "HTTP error"
        assert error.status_code == 500
        assert error.response_text is None
    
    def test_http_error_with_response_text(self):
        """Test HTTP error with response text."""
        error = GeoClientHTTPError("HTTP error", 400, "Bad request")
        assert error.status_code == 400
        assert error.response_text == "Bad request"
    
    def test_http_error_with_details(self):
        """Test HTTP error with details."""
        details = {"url": "http://example.com"}
        error = GeoClientHTTPError("HTTP error", 404, details=details)
        assert error.details == details


class TestGeoClientAuthError:
    """Test cases for GeoClientAuthError."""
    
    def test_auth_error(self):
        """Test authentication error."""
        error = GeoClientAuthError("Unauthorized", 401)
        assert str(error) == "Unauthorized"
        assert error.status_code == 401
        assert isinstance(error, GeoClientHTTPError)


class TestGeoClientAPIError:
    """Test cases for GeoClientAPIError."""
    
    def test_api_error_basic(self):
        """Test basic API error."""
        error = GeoClientAPIError("API error")
        assert str(error) == "API error"
        assert error.geosupport_return_code is None
        assert error.reason_code is None
    
    def test_api_error_with_codes(self):
        """Test API error with return and reason codes."""
        error = GeoClientAPIError("API error", "02", "INVALID_HOUSE_NUMBER")
        assert error.geosupport_return_code == "02"
        assert error.reason_code == "INVALID_HOUSE_NUMBER"
    
    def test_api_error_with_details(self):
        """Test API error with details."""
        details = {"request": {"houseNumber": "999999"}}
        error = GeoClientAPIError("API error", details=details)
        assert error.details == details