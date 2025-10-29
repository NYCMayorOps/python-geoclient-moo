# Example Scripts

This directory contains example scripts demonstrating various use cases for the GeoClient MOO library.

## Scripts

### 1. `basic_usage.py`

Demonstrates the fundamental operations:

- Address geocoding
- BBL and BIN lookups
- Intersection and blockface geocoding
- Place name geocoding
- Basic single-field search

### 2. `batch_geocoding.py`

Shows how to geocode multiple addresses efficiently:

- Batch processing with error handling
- Rate limiting and progress tracking
- Results export to CSV
- Performance metrics

### 3. `advanced_search.py`

Explores the powerful single-field search capabilities:

- Different search input formats
- Advanced search options and parameters
- Results analysis and categorization
- Natural language parsing examples

## Running the Examples

1. **Set up your API credentials:**

   ```bash
   export GEOCLIENT_APP_ID="your_app_id"
   export GEOCLIENT_APP_KEY="your_app_key"
   ```

2. **Install the library:**

   ```bash
   pip install python-geoclient-moo
   ```

3. **Run any example:**

   ```bash
   python basic_usage.py
   python batch_geocoding.py
   python advanced_search.py
   ```

## Getting API Credentials

Visit the [NYC Developer Portal](https://developer.cityofnewyork.us/) to register and get your free API credentials.

## Sample Output

The examples will produce detailed output showing:

- Successful geocoding results with coordinates
- Error handling for invalid inputs
- Performance metrics for batch operations
- Analysis of search result types and levels