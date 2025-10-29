"""Test configuration and fixtures."""

import pytest
import os
from unittest.mock import Mock


def pytest_configure(config):
    """Configure pytest with additional markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring API credentials"
    )


@pytest.fixture
def mock_successful_response():
    """Mock a successful API response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "houseNumber": "314",
        "streetName": "WEST 100 STREET",
        "boroughCode1In": "1",
        "boroughName": "MANHATTAN",
        "zipCode": "10025",
        "latitude": "40.79582646522169",
        "longitude": "-73.96790007529056",
        "xCoordinate": "1008077.62",
        "yCoordinate": "229778.15",
        "bbl": "1018890001",
        "buildingIdentificationNumber": "1079043",
        "communityDistrict": "109",
        "censusTract2010": "243",
        "nta": "MN17",
        "geosupportReturnCode": "00",
        "reasonCode": "",
        "message": "",
    }
    return mock_response


@pytest.fixture
def mock_error_response():
    """Mock an API error response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "geosupportReturnCode": "02",
        "reasonCode": "INVALID_HOUSE_NUMBER",
        "message": "HOUSE NUMBER NOT FOUND",
    }
    return mock_response


@pytest.fixture
def mock_http_error():
    """Mock an HTTP error response."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    return mock_response


@pytest.fixture
def sample_address_data():
    """Sample address response data."""
    return {
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


@pytest.fixture
def sample_bbl_data():
    """Sample BBL response data."""
    return {
        "boroughCode": "1",
        "taxBlock": "1889",
        "taxLot": "1", 
        "bbl": "1018890001",
        "buildingIdentificationNumber": "1079043",
        "houseNumber": "314",
        "streetName": "WEST 100 STREET",
        "latitude": "40.79582646522169",
        "longitude": "-73.96790007529056",
        "geosupportReturnCode": "00",
    }


@pytest.fixture
def sample_search_data():
    """Sample search response data."""
    return {
        "input": "314 west 100 st manhattan",
        "results": [
            {
                "level": 0,
                "status": "EXACT_MATCH",
                "request": {
                    "level": 0,
                    "input": "314 west 100 st manhattan",
                    "taskId": 1,
                    "requestId": "address"
                },
                "response": {
                    "houseNumber": "314",
                    "streetName": "WEST 100 STREET",
                    "boroughCode1In": "1",
                    "latitude": "40.79582646522169",
                    "longitude": "-73.96790007529056",
                    "geosupportReturnCode": "00",
                }
            }
        ],
        "exactMatch": True,
        "similarNames": [],  
    }