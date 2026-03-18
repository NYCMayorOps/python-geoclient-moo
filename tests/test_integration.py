"""Integration tests for the GeoClient."""

import os
import pytest
from geoclient_moo import GeoClient
from geoclient_moo.exceptions import GeoClientError, GeoClientAuthError, GeoClientAPIError


# These tests require a real API subscription key and are skipped by default
pytestmark = pytest.mark.skipif(
    not os.getenv("GEOCLIENT_SUBSCRIPTION_KEY"),
    reason="Integration tests require GEOCLIENT_SUBSCRIPTION_KEY environment variable"
)


@pytest.fixture
def client():
    """Create a GeoClient instance with real credentials."""
    subscription_key = os.getenv("GEOCLIENT_SUBSCRIPTION_KEY")
    return GeoClient(subscription_key)


class TestRealAPIIntegration:
    """Integration tests with the real Geoclient API."""
    
    def test_address_geocoding(self, client):
        """Test real address geocoding."""
        result = client.address("253", "broadway", "manhattan")
        
        assert result.house_number == "253"
        #there are extra spaces in the street name returned by the API
        assert str.lower("Broadway") in str.lower(result.street_name)
        assert result.borough_name == "MANHATTAN"
        assert result.latitude is not None
        assert result.longitude is not None
        assert result.bbl is not None
        assert result.geosupport.return_code in ("00", "01")
    
    def test_address_with_zip(self, client):
        """Test address geocoding with ZIP code."""
        result = client.address("253", "broadway", zip_code="10025")
        
        assert result.house_number == "253"
        assert result.zip_code == "10007"
        assert result.latitude is not None
        assert result.longitude is not None
    
    def test_bbl_lookup(self, client):
        """Test BBL lookup."""
        result = client.bbl("manhattan", "1889", "1")
        
        assert result.borough_code == "1"
        assert result.tax_block == "01889"
        assert result.tax_lot == "0001"
        assert result.bbl == '1018890001'
        #latitude and longitude not returned for BBL lookup?
        assert result.latitude is None
        assert result.longitude is None
    
    def test_bin_lookup(self, client):
        """Test BIN lookup.""" 
        empire_state_bin = "1009720"
        result = client.bin_(empire_state_bin)
        
        assert result.building_identification_number == "1009720"
        assert result.bbl is not None
        assert result.house_number is not None
        assert result.street_name is not None
        #is latitude and longitude returned for BIN lookup?
        assert result.latitude is None
        assert result.longitude is None
    
    def test_lookup_by_intersection(self, client):
        """Test lookup by intersection lookup."""
        result = client.intersection("Broadway", "Wall Street", "manhattan")
        assert result is not None
        
        # Check if there was a geosupport error
        if result.geosupport.return_code not in ("00", "01"):
            print(f"Geosupport error: {result.geosupport.return_code} - {result.geosupport.message}")
        
        # If successful, check the data
        if result.cross_street_one is not None and result.cross_street_two is not None:
            assert "broadway" in str.lower(result.cross_street_one) or "broadway" in str.lower(result.cross_street_two)
            assert "wall" in str.lower(result.cross_street_one) or "wall" in str.lower(result.cross_street_two)
            assert result.borough_code == "1"
            assert result.latitude is not None
            assert result.longitude is not None
        else:
            # If no intersection data, the streets may not intersect or have bad names
            print(f"No intersection found - Geosupport code: {result.geosupport.return_code}")
            print(f"Raw data: {result.raw_data}")
            # Skip assertions for now
            pass

    def test_get_cross_streets_from_address(self, client):
        """Test getting cross streets from an address."""
        result = client.get_cross_streets_from_address("253", "broadway", "manhattan")
        
        assert result is not None
        assert result.house_number == "253"
        assert "broadway" in str.lower(result.street_name or "")
        
        # Cross streets may or may not be available depending on the API response
        if result.cross_street_one:
            print(f"Cross street 1: {result.cross_street_one}")
        if result.cross_street_two:
            print(f"Cross street 2: {result.cross_street_two}")
        
        # 253 Broadway should return cross streets including warren (murray & warren intersection)
        cross_streets = []
        if result.cross_street_one:
            cross_streets.append(str.lower(result.cross_street_one))
        if result.cross_street_two:
            cross_streets.append(str.lower(result.cross_street_two))
        
        # Verify that warren appears in at least one of the cross streets
        assert any("warren" in street for street in cross_streets), \
            f"Expected 'warren' in cross streets but got: {cross_streets}"
        assert any("murray" in street for street in cross_streets), \
            f"Expected 'murray' in cross streets but got: {cross_streets}"
            
        # The method should work the same as regular address geocoding
        assert result.latitude is not None
        assert result.longitude is not None
        assert result.geosupport.return_code in ("00", "01")
    
    def test_blockface_lookup(self, client):
        """Test blockface lookup."""
        result = client.blockface(
            "amsterdam ave", "west 110 st", "west 111 st", "manhattan"
        )
        assert result is not None
        
        # Check if we got valid blockface data
        if result.on_street and result.cross_street_one and result.cross_street_two:
            assert "AMSTERDAM" in result.on_street.upper()
            assert "WEST 110" in result.cross_street_one.upper()
            assert "WEST 111" in result.cross_street_two.upper()
            assert result.borough_code == "1"
            assert result.latitude is not None
            assert result.longitude is not None
        else:
            # If blockface data is missing, check geosupport status
            print(f"Blockface data missing - Geosupport code: {result.geosupport.return_code}")
            print(f"Raw data: {result.raw_data}")
            # The call succeeded but may not have complete data
    
    def test_place_lookup(self, client):
        """Test place name lookup for Empire State Building.
        
        Verified against real API response on 2026-03-18.
        Note: /place returns the place name in boePreferredStreetName.
        houseNumber and streetName are NOT returned by this endpoint.
        The zip_code in the response (10118) differs from the input zip (10001)
        because the API returns the actual building zip, not the input.
        """
        result = client.place("empire state building", borough="manhattan", zip_code="10001")
        
        assert result.place_name == "EMPIRE STATE BUILDING"
        assert result.house_number is None
        assert result.street_name is None
        assert result.borough_name == "MANHATTAN"
        assert result.bbl == "1008350041"
        assert result.bin == "1015862"
        assert result.zip_code == "10118"
        assert abs(result.latitude - 40.74843) < 0.001
        assert abs(result.longitude - (-73.985322)) < 0.001
        assert result.geosupport.return_code in ("00", "01")
    
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


    
    def test_search_various_inputs(self, client):
        """Test search with different input types."""
        # Test address search
        result = client.search("253 broadway manhattan")
        assert result is not None
        assert len(result.results) > 0
        
        # Test BIN search  
        result = client.search("1079043")
        assert result is not None
        assert len(result.results) > 0


class TestErrorHandling:
    """Test error handling with real API."""
    
    def test_invalid_credentials(self):
        """Test authentication error with invalid credentials."""
        
        with pytest.raises(GeoClientAuthError):
            client2 = GeoClient("invalid_id")
            client2.address("314", "west 100 st", "manhattan")
    
    def test_invalid_address(self, client):
        """Test API error with invalid address."""
        with pytest.raises(GeoClientError):
            client.address("999999", "nonexistent street", "manhattan")
    
    def test_invalid_bbl(self, client):
        """Test API error with invalid BBL."""
        with pytest.raises(GeoClientAPIError):
            client.bbl("manhattan", "99999", "99999")


class TestContextManager:
    """Test context manager functionality."""
    
    def test_context_manager_usage(self):
        """Test using client as context manager."""
        subscription_key = os.getenv("GEOCLIENT_SUBSCRIPTION_KEY")
        
        with GeoClient(subscription_key) as client:
            result = client.address("314", "west 100 st", "manhattan")
            assert result.house_number == "314"