"""
Batch geocoding example for the GeoClient MOO library.

This script demonstrates how to geocode multiple addresses efficiently,
with proper error handling and progress tracking.

Before running this script, set your API subscription key as an environment variable:
    $env:GEOCLIENT_SUBSCRIPTION_KEY = "your_subscription_key"
"""

import os
import csv
import time
from typing import List, Dict, Any
from geoclient import GeoClient
from geoclient.exceptions import GeoClientError


def load_addresses_from_csv(filename: str) -> List[Dict[str, str]]:
    """
    Load addresses from a CSV file.
    
    Expected columns (case-insensitive): house_number, street, borough
    
    Args:
        filename: Path to the CSV file
        
    Returns:
        List of address dictionaries ready for batch_geocode_addresses()
    """
    addresses = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # Normalize column names to lowercase with underscores
        for row in reader:
            normalized = {k.strip().lower().replace(' ', '_'): v.strip() for k, v in row.items()}
            addresses.append({
                'house_number': normalized['house_number'],
                'street': normalized['street'],
                'borough': normalized['borough'],
            })
    return addresses


def batch_geocode_addresses(
    addresses: List[Dict[str, str]], 
    client: GeoClient,
    delay: float = 0.1
) -> List[Dict[str, Any]]:
    """
    Geocode a batch of addresses with error handling and rate limiting.
    
    Args:
        addresses: List of address dictionaries with keys: house_number, street, borough
        client: Initialized GeoClient instance
        delay: Delay between requests in seconds (for rate limiting)
        
    Returns:
        List of geocoding results with success/error information
    """
    results = []
    
    for i, addr in enumerate(addresses, 1):
        print(f"Processing {i}/{len(addresses)}: {addr['house_number']} {addr['street']}, {addr['borough']}")
        
        try:
            result = client.address(
                addr['house_number'], 
                addr['street'], 
                addr['borough']
            )
            
            # Successful geocoding
            results.append({
                'input_house_number': addr['house_number'],
                'input_street': addr['street'],
                'input_borough': addr['borough'],
                'success': True,
                'latitude': result.latitude,
                'longitude': result.longitude,
                'normalized_address': f"{result.house_number} {result.street_name}",
                'normalized_borough': result.borough_name,
                'zip_code': result.zip_code,
                'bbl': result.bbl,
                'bin': result.bin,
                'community_district': result.community_district,
                'cross_street_one': result.cross_street_one,
                'cross_street_two': result.cross_street_two,
                'error_message': None,
                'geosupport_return_code': result.geosupport.return_code,
            })
            
        except GeoClientError as e:
            # Failed geocoding
            results.append({
                'input_house_number': addr['house_number'],
                'input_street': addr['street'],
                'input_borough': addr['borough'],
                'success': False,
                'latitude': None,
                'longitude': None,
                'normalized_address': None,
                'normalized_borough': None,
                'zip_code': None,
                'bbl': None,
                'bin': None,
                'community_district': None,
                'error_message': str(e),
                'geosupport_return_code': getattr(e, 'geosupport_return_code', None),
            })
            print(f"  ❌ Error: {e}")
        
        # Rate limiting
        if delay > 0:
            time.sleep(delay)
    
    return results


def geocode_csv(input_file: str, output_file: str, delay: float = 0.1) -> None:
    """
    Geocode addresses from an input CSV and write results to an output CSV.

    The input CSV must have columns: house_number, street, borough
    (column names are case-insensitive; spaces or underscores both accepted).

    Args:
        input_file: Path to the input CSV file containing addresses.
        output_file: Path to write the geocoded results CSV.
        delay: Seconds to wait between API requests (default 0.1).
    """
    addresses = load_addresses_from_csv(input_file)
    print(f"Loaded {len(addresses)} addresses from {input_file}")

    with GeoClient() as client:
        results = batch_geocode_addresses(addresses, client, delay=delay)

    save_results_to_csv(results, output_file)

    successful = sum(1 for r in results if r['success'])
    print(f"Done: {successful}/{len(results)} geocoded successfully → {output_file}")


def save_results_to_csv(results: List[Dict[str, Any]], filename: str) -> None:
    """Save geocoding results to a CSV file."""
    if not results:
        print("No results to save")
        return
    
    fieldnames = results[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Results saved to {filename}")


def main():
    """Demonstrate batch geocoding."""

    # Initialize the client (reads GEOCLIENT_SUBSCRIPTION_KEY from environment)
    # Sample addresses to geocode
    sample_addresses = [
        {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
        {"house_number": "350", "street": "5th ave", "borough": "manhattan"},
        {"house_number": "1", "street": "wall st", "borough": "manhattan"},
        {"house_number": "1", "street": "times square", "borough": "manhattan"},
        {"house_number": "120", "street": "broadway", "borough": "manhattan"},
        {"house_number": "33", "street": "thomas st", "borough": "manhattan"},
        {"house_number": "185", "street": "broadway", "borough": "manhattan"},
        {"house_number": "75", "street": "broad st", "borough": "manhattan"},
        {"house_number": "invalid", "street": "fake street", "borough": "manhattan"},  # This will fail
        {"house_number": "200", "street": "vesey st", "borough": "manhattan"},
    ]
    
    print("🏢 Batch Geocoding Example")
    print("=" * 50)
    print(f"Geocoding {len(sample_addresses)} addresses...")
    
    # Perform batch geocoding
    with GeoClient() as client:
        start_time = time.time()
        
        results = batch_geocode_addresses(
            addresses=sample_addresses,
            client=client,
            delay=0.1  # 100ms delay between requests
        )
        
        end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Batch Geocoding Summary")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"Total addresses: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/len(results)*100:.1f}%")
    print(f"Total time: {end_time - start_time:.1f} seconds")
    print(f"Average time per address: {(end_time - start_time)/len(results):.2f} seconds")
    
    # Show successful results
    if successful > 0:
        print(f"\n✅ Successfully Geocoded Addresses:")
        print("-" * 40)
        for result in results:
            if result['success']:
                print(f"  {result['normalized_address']}, {result['normalized_borough']}")
                print(f"    Coordinates: {result['latitude']:.6f}, {result['longitude']:.6f}")
                print(f"    BBL: {result['bbl']}, ZIP: {result['zip_code']}")
                print(f"    Cross Streets: {result.get('cross_street_one', '')}, {result.get('cross_street_two', '')}")
                print()
    
    # Show failed results
    if failed > 0:
        print(f"❌ Failed to Geocode:")
        print("-" * 25)
        for result in results:
            if not result['success']:
                print(f"  {result['input_house_number']} {result['input_street']}, {result['input_borough']}")
                print(f"    Error: {result['error_message']}")
                print()
    
    # Save results to CSV
    output_filename = "geocoding_results.csv"
    save_results_to_csv(results, output_filename)
    
    print("✅ Batch geocoding completed!")


if __name__ == "__main__":
    main()