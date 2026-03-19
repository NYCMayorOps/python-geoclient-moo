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