"""Integration tests for the GeoClient."""

import os
import pytest
from geoclient_moo import GeoClient
from geoclient_moo.exceptions import GeoClientError, GeoClientAuthError


# These tests require real API credentials and are skipped by default
pytestmark = pytest.mark.skipif(
    not (os.getenv("GEOCLIENT_APP_ID") and os.getenv("GEOCLIENT_APP_KEY")),
    reason="Integration tests require GEOCLIENT_APP_ID and GEOCLIENT_APP_KEY environment variables"
)


@pytest.fixture
def client():
    """Create a GeoClient instance with real credentials."""
    app_id = os.getenv("GEOCLIENT_APP_ID")
    app_key = os.getenv("GEOCLIENT_APP_KEY")
    return GeoClient(app_id, app_key)


class TestRealAPIIntegration:
    """Integration tests with the real Geoclient API."""
    
    def test_address_geocoding(self, client):
        """Test real address geocoding."""
        result = client.address("314", "west 100 st", "manhattan")
        
        assert result.house_number == "314"
        assert "WEST 100" in result.street_name
        assert result.borough_name == "MANHATTAN"
        assert result.latitude is not None
        assert result.longitude is not None
        assert result.bbl is not None
        assert result.geosupport.return_code in ("00", "01")
    
    def test_address_with_zip(self, client):
        """Test address geocoding with ZIP code."""
        result = client.address("314", "west 100 st", zip_code="10025")
        
        assert result.house_number == "314"
        assert result.zip_code == "10025"
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_bbl_lookup(self, client):
        """Test BBL lookup."""
        result = client.bbl("manhattan", "1889", "1")
        
        assert result.borough_code == "1"
        assert result.tax_block == "1889"
        assert result.tax_lot == "1"
        assert result.bbl == "1018890001"
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_bin_lookup(self, client):
        """Test BIN lookup.""" 
        result = client.bin_("1079043")
        
        assert result.building_identification_number == "1079043"
        assert result.bbl is not None
        assert result.house_number is not None
        assert result.street_name is not None
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_intersection_lookup(self, client):
        """Test intersection lookup."""
        result = client.intersection("broadway", "west 100 st", "manhattan")
        
        assert "BROADWAY" in result.cross_street_one
        assert "WEST 100" in result.cross_street_two
        assert result.borough_code == "1"
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_blockface_lookup(self, client):
        """Test blockface lookup."""
        result = client.blockface(
            "amsterdam ave", "west 110 st", "west 111 st", "manhattan"
        )
        
        assert "AMSTERDAM" in result.on_street
        assert "WEST 110" in result.cross_street_one
        assert "WEST 111" in result.cross_street_two
        assert result.borough_code == "1"
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_place_lookup(self, client):
        """Test place name lookup."""
        result = client.place("empire state building", "manhattan")
        
        assert result.place_name is not None
        assert result.borough_name == "MANHATTAN"
        assert result.latitude is not None
        assert result.longitude is not None
        assert result.bbl is not None
    
    def test_search_address(self, client):
        """Test single-field search with address."""
        result = client.search("314 west 100 st manhattan")
        
        assert result.input == "314 west 100 st manhattan"
        assert len(result.results) > 0
        
        # Find exact match result
        exact_match = None
        for search_result in result.results:
            if search_result.status == "EXACT_MATCH":
                exact_match = search_result
                break
        
        assert exact_match is not None
        assert exact_match.response is not None
        assert "houseNumber" in exact_match.response
    
    def test_search_intersection(self, client):
        """Test single-field search with intersection."""
        result = client.search("broadway and west 100 st")
        
        assert "broadway and west 100 st" in result.input.lower()
        assert len(result.results) > 0
    
    def test_search_with_options(self, client):
        """Test search with optional parameters."""
        result = client.search(
            "314 west 100 st manhattan",
            return_tokens=True,
            return_policy=True,
            exact_match_for_single_success=True,
        )
        
        assert result.input == "314 west 100 st manhattan"
        assert len(result.results) > 0


class TestErrorHandling:
    """Test error handling with real API."""
    
    def test_invalid_credentials(self):
        """Test authentication error with invalid credentials."""
        client = GeoClient("invalid_id", "invalid_key")
        
        with pytest.raises(GeoClientAuthError):
            client.address("314", "west 100 st", "manhattan")
    
    def test_invalid_address(self, client):
        """Test API error with invalid address."""
        with pytest.raises(GeoClientError):
            client.address("999999", "nonexistent street", "manhattan")
    
    def test_invalid_bbl(self, client):
        """Test API error with invalid BBL."""
        with pytest.raises(GeoClientError):
            client.bbl("manhattan", "99999", "99999")


class TestContextManager:
    """Test context manager functionality."""
    
    def test_context_manager_usage(self):
        """Test using client as context manager."""
        app_id = os.getenv("GEOCLIENT_APP_ID")
        app_key = os.getenv("GEOCLIENT_APP_KEY")
        
        with GeoClient(app_id, app_key) as client:
            result = client.address("314", "west 100 st", "manhattan")
            assert result.house_number == "314"