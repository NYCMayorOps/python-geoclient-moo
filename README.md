# Python Geoclient MOO

A comprehensive Python wrapper for the NYC OTI Geoclient 2.0 API, providing easy access to New York City's official geocoding service.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The NYC Geoclient API provides developer-friendly access to the Department of City Planning's official geocoding service (Geosupport). This Python wrapper makes it easy to geocode NYC addresses, intersections, places, and more.

## Features

- 🏢 **Address Geocoding**: Convert NYC addresses to coordinates and property information
- 🔢 **BBL/BIN Lookups**: Get property details by Borough-Block-Lot or Building Identification Number  
- 🛣️ **Street Operations**: Geocode intersections and blockfaces
- 🏛️ **Place Names**: Find coordinates for well-known NYC locations
- 🔍 **Single-Field Search**: Parse natural language location queries
- 🛡️ **Type Safety**: Full type hints and response models
- ⚡ **Robust Error Handling**: Comprehensive exception handling with retries
- 🧪 **Well Tested**: Extensive unit and integration test coverage

## Installation

```bash
pip install python-geoclient-moo
```

## Quick Start

```python
from geoclient import GeoClient

# Initialize the client with your API credentials
client = GeoClient(
    app_id="your_app_id",
    app_key="your_app_key"
)

# Geocode an address
result = client.address("314", "west 100 st", "manhattan")
print(f"Coordinates: {result.latitude}, {result.longitude}")
print(f"BBL: {result.bbl}")

# Use as a context manager (recommended)
with GeoClient("your_app_id", "your_app_key") as client:
    result = client.search("empire state building")
    print(f"Found: {result.results[0].response}")
```

## Getting API Credentials

To use the Geoclient API, you need to register for free API credentials:

1. Visit the [NYC Developer Portal](https://developer.cityofnewyork.us/)
2. Create an account and register a new application
3. Subscribe to the Geoclient API
4. Note your `app_id` and `app_key`

## API Methods

### Address Geocoding

```python
# Geocode with borough
result = client.address("314", "west 100 st", "manhattan")

# Geocode with ZIP code
result = client.address("314", "west 100 st", zip_code="10025")

# Access response data
print(f"Address: {result.house_number} {result.street_name}")
print(f"Borough: {result.borough_name}")
print(f"Coordinates: {result.latitude}, {result.longitude}")
print(f"BBL: {result.bbl}, BIN: {result.bin}")
```

### Property Lookups

```python
# Look up by Borough-Block-Lot (BBL)
result = client.bbl("manhattan", "1889", "1")
print(f"Address: {result.house_number} {result.street_name}")

# Look up by Building Identification Number (BIN)
result = client.bin_("1079043")
print(f"BBL: {result.bbl}")
```

### Street Operations

```python
# Geocode intersection
result = client.intersection("broadway", "west 100 st", "manhattan")
print(f"Intersection: {result.latitude}, {result.longitude}")

# Get blockface information
result = client.blockface(
    on_street="amsterdam ave",
    cross_street_one="west 110 st", 
    cross_street_two="west 111 st",
    borough="manhattan"
)
print(f"Segment length: {result.segment_length} feet")
```

### Place Names

```python
# Geocode well-known places
result = client.place("empire state building", "manhattan")
print(f"Place: {result.place_name}")
print(f"Address: {result.house_number} {result.street_name}")
```

### Single-Field Search

The search endpoint can parse various input formats:

```python
# Address search
result = client.search("314 west 100 st manhattan")

# Intersection search  
result = client.search("broadway and west 100 st")

# BBL search
result = client.search("1018890001")

# BIN search
result = client.search("1079043")

# Blockface search
result = client.search("broadway between west 100 st and west 101 st")

# Place search
result = client.search("empire state building")

# Process results
for search_result in result.results:
    if search_result.status == "EXACT_MATCH":
        print(f"Found exact match: {search_result.response}")
```

### Search Options

Customize search behavior with optional parameters:

```python
result = client.search(
    "314 west 100 st",
    exact_match_for_single_success=True,  # Treat single result as exact match
    exact_match_max_level=3,              # Maximum search levels
    return_tokens=True,                   # Return parsed input tokens
    return_rejections=True,               # Include rejected results
    similar_names_distance=8              # Levenshtein distance for similar names
)
```

## Response Models

All API methods return typed response objects with parsed data:

```python
result = client.address("314", "west 100 st", "manhattan")

# Basic address info
print(result.house_number)      # "314"
print(result.street_name)       # "WEST 100 STREET" 
print(result.borough_name)      # "MANHATTAN"
print(result.zip_code)          # "10025"

# Geographic coordinates
print(result.latitude)          # 40.79582646522169
print(result.longitude)         # -73.96790007529056
print(result.x_coordinate)      # State plane coordinate
print(result.y_coordinate)      # State plane coordinate

# Property identifiers
print(result.bbl)               # "1018890001"
print(result.bin)               # "1079043"

# Administrative areas
print(result.community_district)  # "109"
print(result.census_tract)        # "243"

# Processing status
print(result.geosupport.return_code)  # "00" (success)
print(result.geosupport.message)      # Status message

# Raw API response (if needed)
print(result.raw_data)          # Complete API response dict
```

## Error Handling

The library provides comprehensive error handling:

```python
from geoclient.exceptions import (
    GeoClientError,           # Base exception
    GeoClientHTTPError,       # HTTP errors (4xx, 5xx)
    GeoClientAuthError,       # Authentication errors (401, 403)
    GeoClientAPIError,        # Geosupport API errors
)

try:
    result = client.address("999999", "invalid street", "manhattan")
except GeoClientAuthError:
    print("Check your API credentials")
except GeoClientAPIError as e:
    print(f"Geosupport error: {e.geosupport_return_code} - {e.message}")
except GeoClientHTTPError as e:
    print(f"HTTP error {e.status_code}: {e.message}")
except GeoClientError as e:
    print(f"General error: {e.message}")
```

## Configuration

Customize client behavior:

```python
client = GeoClient(
    app_id="your_app_id",
    app_key="your_app_key",
    base_url="https://api.nyc.gov/geo/geoclient/v2/",  # Custom base URL
    timeout=30.0,           # Request timeout in seconds  
    retries=3,              # Number of retries for failed requests
    retry_delay=1.0,        # Delay between retries in seconds  
)
```

## Advanced Usage

### Batch Processing

```python
addresses = [
    ("314", "west 100 st", "manhattan"),
    ("350", "5th ave", "manhattan"),
    ("1", "wall st", "manhattan"),
]

results = []
with GeoClient("app_id", "app_key") as client:
    for house_num, street, borough in addresses:
        try:
            result = client.address(house_num, street, borough)
            results.append({
                'input': f"{house_num} {street}",
                'lat': result.latitude,
                'lng': result.longitude,
                'bbl': result.bbl
            })
        except GeoClientError as e:
            print(f"Error geocoding {house_num} {street}: {e}")
```

### Borough Validation

```python
# The client accepts various borough formats:
client.address("314", "west 100 st", "manhattan")    # Full name
client.address("314", "west 100 st", "Manhattan")    # Title case
client.address("314", "west 100 st", "MANHATTAN")    # Upper case
client.address("314", "west 100 st", "1")            # Borough code
client.address("314", "west 100 st", "si")           # Staten Island abbreviation

# Valid borough names/codes:
# Manhattan: "manhattan", "1"
# Bronx: "bronx", "2" 
# Brooklyn: "brooklyn", "3"
# Queens: "queens", "4"
# Staten Island: "staten island", "si", "5"
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=geoclient --cov-report=html

# Run integration tests (requires API credentials)
export GEOCLIENT_APP_ID="your_app_id"
export GEOCLIENT_APP_KEY="your_app_key"
pytest tests/test_integration.py -v
```

## API Reference

For complete API documentation, see the [official Geoclient documentation](https://maps.nyc.gov/geoclient/v2/doc).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 **Email**: [gis-development@doitt.nyc.gov](mailto:gis-development@doitt.nyc.gov)
- 🐛 **Issues**: [GitHub Issues](https://github.com/NYCMayorOps/python-geoclient-moo/issues)
- 📖 **Documentation**: [Official Geoclient Docs](https://maps.nyc.gov/geoclient/v2/doc)

## Changelog

### v0.1.0 (2024-10-29)

- Initial release
- Full support for all Geoclient 2.0 API endpoints
- Comprehensive error handling and type safety
- Extensive test coverage
- Complete documentation and examples
