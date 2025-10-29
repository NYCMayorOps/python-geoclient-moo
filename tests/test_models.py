"""Unit tests for the GeoClient models."""

import pytest
from geoclient_moo.models import (
    AddressResponse,
    BBLResponse,
    BINResponse,
    BlockfaceResponse,
    IntersectionResponse,
    PlaceResponse,
    SearchResponse,
    SearchResult,
    GeosupportInfo,
    _safe_float,
    _safe_int,
)


class TestSafeConversions:
    """Test cases for safe conversion functions."""
    
    def test_safe_float(self):
        """Test safe float conversion."""
        assert _safe_float("123.45") == 123.45
        assert _safe_float(123.45) == 123.45
        assert _safe_float("123") == 123.0
        assert _safe_float(None) is None
        assert _safe_float("") is None
        assert _safe_float("invalid") is None
        assert _safe_float([1, 2, 3]) is None
    
    def test_safe_int(self):
        """Test safe int conversion."""
        assert _safe_int("123") == 123
        assert _safe_int(123) == 123
        assert _safe_int("123.0") == 123
        assert _safe_int(None) is None
        assert _safe_int("") is None
        assert _safe_int("invalid") is None
        assert _safe_int("123.45") is None  # Should fail for floats


class TestGeosupportInfo:
    """Test cases for GeosupportInfo model."""
    
    def test_default_creation(self):
        """Test default GeosupportInfo creation."""
        info = GeosupportInfo()
        assert info.return_code is None
        assert info.reason_code is None
        assert info.message is None
        assert info.return_code_1a is None
    
    def test_creation_with_values(self):
        """Test GeosupportInfo creation with values."""
        info = GeosupportInfo(
            return_code="00",
            reason_code="",
            message="Success",
        )
        assert info.return_code == "00"
        assert info.reason_code == ""
        assert info.message == "Success"


class TestAddressResponse:
    """Test cases for AddressResponse model."""
    
    def test_from_dict_basic(self):
        """Test AddressResponse creation from dictionary."""
        data = {
            "houseNumber": "314",
            "streetName": "WEST 100 STREET",
            "boroughCode1In": "1",
            "boroughName": "MANHATTAN",
            "zipCode": "10025",
            "latitude": "40.79582646522169",
            "longitude": "-73.96790007529056",
            "bbl": "1018890001",
            "buildingIdentificationNumber": "1079043",
            "geosupportReturnCode": "00",
        }
        
        response = AddressResponse.from_dict(data)
        
        assert response.house_number == "314"
        assert response.street_name == "WEST 100 STREET"
        assert response.borough_code == "1"
        assert response.borough_name == "MANHATTAN"
        assert response.zip_code == "10025"
        assert response.latitude == 40.79582646522169
        assert response.longitude == -73.96790007529056
        assert response.bbl == "1018890001"
        assert response.bin == "1079043"
        assert response.geosupport.return_code == "00"
        assert response.raw_data == data
    
    def test_from_dict_with_function_1b_codes(self):
        """Test AddressResponse with Function 1B return codes."""
        data = {
            "geosupportReturnCode": "00",
            "geosupportReturnCode2": "00",  # Function 1A
            "returnCode1e": "00",  # Function 1E
            "reasonCode2": "",
            "reasonCode1e": "",
        }
        
        response = AddressResponse.from_dict(data)
        
        assert response.geosupport.return_code == "00"
        assert response.geosupport.return_code_1a == "00"
        assert response.geosupport.return_code_1e == "00"
    
    def test_from_dict_missing_fields(self):
        """Test AddressResponse with missing optional fields."""
        data = {"geosupportReturnCode": "00"}
        
        response = AddressResponse.from_dict(data)
        
        assert response.house_number is None
        assert response.latitude is None
        assert response.geosupport.return_code == "00"


class TestBBLResponse:
    """Test cases for BBLResponse model."""
    
    def test_from_dict_basic(self):
        """Test BBLResponse creation from dictionary."""
        data = {
            "boroughCode": "1",
            "taxBlock": "1889",
            "taxLot": "1",
            "bbl": "1018890001",
            "buildingIdentificationNumber": "1079043",
            "numBuildingsOnLot": "1",
            "latitude": "40.79582646522169",
            "longitude": "-73.96790007529056",
            "geosupportReturnCode": "00",
        }
        
        response = BBLResponse.from_dict(data)
        
        assert response.borough_code == "1"
        assert response.tax_block == "1889"
        assert response.tax_lot == "1"
        assert response.bbl == "1018890001"
        assert response.building_identification_number == "1079043"
        assert response.num_buildings_on_lot == 1
        assert response.latitude == 40.79582646522169
        assert response.longitude == -73.96790007529056


class TestBINResponse:
    """Test cases for BINResponse model."""
    
    def test_from_dict_basic(self):
        """Test BINResponse creation from dictionary."""
        data = {
            "buildingIdentificationNumber": "1079043",
            "bbl": "1018890001",
            "houseNumber": "314",
            "streetName": "WEST 100 STREET",
            "boroughCode": "1",
            "boroughName": "MANHATTAN",
            "latitude": "40.79582646522169",
            "longitude": "-73.96790007529056",
            "geosupportReturnCode": "00",
        }
        
        response = BINResponse.from_dict(data)
        
        assert response.building_identification_number == "1079043"
        assert response.bbl == "1018890001"
        assert response.house_number == "314"
        assert response.street_name == "WEST 100 STREET"
        assert response.borough_code == "1"
        assert response.borough_name == "MANHATTAN"


class TestBlockfaceResponse:
    """Test cases for BlockfaceResponse model."""
    
    def test_from_dict_basic(self):
        """Test BlockfaceResponse creation from dictionary."""
        data = {
            "onStreet": "AMSTERDAM AVENUE",
            "crossStreetOne": "WEST 110 STREET",
            "crossStreetTwo": "WEST 111 STREET",
            "boroughCode": "1",
            "latitude": "40.800611",
            "longitude": "-73.961681",
            "segmentLength": "200.5",
            "streetWidth": "60.0",
            "geosupportReturnCode": "00",
        }
        
        response = BlockfaceResponse.from_dict(data)
        
        assert response.on_street == "AMSTERDAM AVENUE"
        assert response.cross_street_one == "WEST 110 STREET"
        assert response.cross_street_two == "WEST 111 STREET"
        assert response.borough_code == "1"
        assert response.segment_length == 200.5
        assert response.street_width == 60.0


class TestIntersectionResponse:
    """Test cases for IntersectionResponse model."""
    
    def test_from_dict_basic(self):
        """Test IntersectionResponse creation from dictionary."""
        data = {
            "crossStreetOne": "BROADWAY",
            "crossStreetTwo": "WEST 100 STREET",
            "boroughCode": "1",
            "latitude": "40.79582646522169",
            "longitude": "-73.96790007529056",
            "geosupportReturnCode": "00",
        }
        
        response = IntersectionResponse.from_dict(data)
        
        assert response.cross_street_one == "BROADWAY"
        assert response.cross_street_two == "WEST 100 STREET"
        assert response.borough_code == "1"
        assert response.latitude == 40.79582646522169
        assert response.longitude == -73.96790007529056


class TestPlaceResponse:
    """Test cases for PlaceResponse model."""
    
    def test_from_dict_basic(self):
        """Test PlaceResponse creation from dictionary."""
        data = {
            "inputName": "EMPIRE STATE BUILDING",
            "houseNumber": "350",
            "streetName": "5 AVENUE",
            "boroughCode1In": "1",
            "boroughName": "MANHATTAN",
            "zipCode": "10118",
            "latitude": "40.748441",
            "longitude": "-73.985664",
            "bbl": "1008160035",
            "buildingIdentificationNumber": "1001026",
            "geosupportReturnCode": "00",
        }
        
        response = PlaceResponse.from_dict(data)
        
        assert response.place_name == "EMPIRE STATE BUILDING"
        assert response.house_number == "350"
        assert response.street_name == "5 AVENUE"
        assert response.borough_name == "MANHATTAN"
        assert response.bbl == "1008160035"
        assert response.bin == "1001026"


class TestSearchResult:
    """Test cases for SearchResult model."""
    
    def test_from_dict_basic(self):
        """Test SearchResult creation from dictionary."""
        data = {
            "level": 0,
            "status": "EXACT_MATCH",
            "request": {"input": "314 west 100 st manhattan"},
            "response": {"houseNumber": "314", "streetName": "WEST 100 STREET"},
        }
        
        result = SearchResult.from_dict(data)
        
        assert result.level == 0
        assert result.status == "EXACT_MATCH"
        assert result.request == {"input": "314 west 100 st manhattan"}
        assert "houseNumber" in result.response


class TestSearchResponse:
    """Test cases for SearchResponse model."""
    
    def test_from_dict_basic(self):
        """Test SearchResponse creation from dictionary."""
        data = {
            "input": "314 west 100 st manhattan",
            "results": [
                {
                    "level": 0,
                    "status": "EXACT_MATCH",
                    "request": {"input": "314 west 100 st manhattan"},
                    "response": {"houseNumber": "314"},
                }
            ],
            "exactMatch": True,
            "similarNames": [],
        }
        
        response = SearchResponse.from_dict(data)
        
        assert response.input == "314 west 100 st manhattan"
        assert len(response.results) == 1
        assert response.results[0].status == "EXACT_MATCH"
        assert response.exact_match is True
        assert response.similar_names == []
    
    def test_from_dict_no_results(self):
        """Test SearchResponse with no results."""
        data = {
            "input": "invalid address",
            "exactMatch": False,
        }
        
        response = SearchResponse.from_dict(data)
        
        assert response.input == "invalid address"
        assert response.results == []
        assert response.exact_match is False