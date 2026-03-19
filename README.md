# Python Geoclient MOO

- Author @SteveScott

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
4. There are two keys, a primary and secondary key. Take the first key and
save it as the enviroment variable GEOCLIENT_SUBSCRIPTION_KEY. 

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

### Batch Geocoding

The library includes a batch geocoding module for processing many addresses at once, with built-in rate limiting and error handling.

#### CSV-to-CSV (simplest)

Geocode an entire CSV file in one call:

```python
from geoclient import geocode_csv

# Input CSV must have columns: house_number, street, borough
geocode_csv("addresses.csv", "results.csv", delay=0.1)
```

#### Programmatic batch

For more control, use `batch_geocode_addresses` with your own client:

```python
from geoclient import GeoClient, batch_geocode_addresses

addresses = [
    {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
    {"house_number": "350", "street": "5th ave", "borough": "manhattan"},
]

with GeoClient() as client:
    results = batch_geocode_addresses(addresses, client, delay=0.1)

for r in results:
    if r["success"]:
        print(f"{r['normalized_address']}: {r['latitude']}, {r['longitude']}")
    else:
        print(f"FAILED {r['input_house_number']} {r['input_street']}: {r['error_message']}")
```

#### Load addresses from CSV

```python
from geoclient import load_addresses_from_csv

addresses = load_addresses_from_csv("addresses.csv")
# Returns: [{"house_number": "314", "street": "west 100 st", "borough": "manhattan"}, ...]
```

Column names are case-insensitive and accept spaces or underscores (e.g., `House Number` or `house_number`).

#### Save results to CSV

```python
from geoclient import save_results_to_csv

save_results_to_csv(results, "output.csv")
```

#### Result fields

Each result dict contains:

| Field | Success | Failure |
|---|---|---|
| `input_house_number`, `input_street`, `input_borough` | Original input | Original input |
| `success` | `True` | `False` |
| `latitude`, `longitude` | Coordinates | `None` |
| `normalized_address`, `normalized_borough` | Geosupport-normalized | `None` |
| `zip_code`, `bbl`, `bin`, `community_district` | Property info | `None` |
| `cross_street_one`, `cross_street_two` | Cross streets | `None` |
| `error_message` | `None` | Error description |
| `geosupport_return_code` | `"00"` | Error code or `None` |

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

- 📧 **Email**: [Steve Scott](mailto:steve@stevescott.blog)
- 🐛 **Issues**: [GitHub Issues](https://github.com/NYCMayorOps/python-geoclient-moo/issues)
- 📖 **Documentation**: [Official Geoclient Docs](https://maps.nyc.gov/geoclient/v2/doc)

## Changelog

### v1.0.0 (2026-03-19)

- Initial release
- Full support for all Geoclient 2.0 API endpoints
- Comprehensive error handling and type safety
- Extensive test coverage
- Complete documentation and examples
