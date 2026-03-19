"""
Basic usage examples for the GeoClient MOO library.

This script demonstrates the most common use cases:
- Address geocoding
- Property lookups (BBL/BIN)
- Intersection and blockface geocoding
- Place name geocoding
- Single-field search

Before running this script, set your API subscription key as a Windows environment variable:
    $env:GEOCLIENT_SUBSCRIPTION_KEY = "your_subscription_key"
"""

import os
from geoclient import GeoClient
from geoclient.exceptions import GeoClientError


def main():
    """Demonstrate basic GeoClient usage."""
    
    # Initialize the client (reads GEOCLIENT_SUBSCRIPTION_KEY from environment)
    with GeoClient() as client:
        
        print("🏢 NYC Geoclient API Examples")
        print("=" * 50)
        
        # Example 1: Address Geocoding
        print("\n1. Address Geocoding")
        print("-" * 25)
        
        try:
            result = client.address("314", "west 100 st", "manhattan")
            print(f"Address: {result.house_number} {result.street_name}")
            print(f"Borough: {result.borough_name}")
            print(f"ZIP Code: {result.zip_code}")
            print(f"Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
            print(f"BBL: {result.bbl}")
            print(f"BIN: {result.bin}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 2: BBL Lookup
        print("\n2. BBL (Borough-Block-Lot) Lookup")
        print("-" * 35)
        
        try:
            result = client.bbl("manhattan", "1889", "1")
            print(f"BBL: {result.bbl}")
            print(f"Address: {result.house_number} {result.street_name}")
            print(f"BIN: {result.building_identification_number}")
            #print(f"Coordinates: {result.latitude}, {result.longitude}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 3: BIN Lookup
        print("\n3. BIN (Building Identification Number) Lookup")
        print("-" * 45)
        
        try:
            result = client.bin_("1079043")
            print(f"BIN: {result.building_identification_number}")
            print(f"Address: {result.house_number} {result.street_name}")
            print(f"Borough: {result.borough_name}")
            print(f"BBL: {result.bbl}")
            #print(f"Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 4: Intersection Geocoding
        print("\n4. Intersection Geocoding")
        print("-" * 27)
        
        try:
            result = client.intersection("broadway", "west 100 st", "manhattan")
            print(f"Intersection: {result.cross_street_one} & {result.cross_street_two}")
            print(f"Borough Code: {result.borough_code}")
            #print(f"Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 5: Blockface Information
        print("\n5. Blockface Information")
        print("-" * 25)
        
        try:
            result = client.blockface(
                on_street="amsterdam ave",
                cross_street_one="west 110 st",
                cross_street_two="west 111 st",
                borough="manhattan"
            )
            print(f"Street: {result.on_street}")
            print(f"Between: {result.cross_street_one} and {result.cross_street_two}")
            print(f"Segment Length: {result.segment_length} feet")
            print(f"Street Width: {result.street_width} feet")
            #print(f"Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 6: Place Name Geocoding
        print("\n6. Place Name Geocoding")
        print("-" * 25)
        
        try:
            result = client.place("empire state building", "manhattan")
            print(f"Place: {result.place_name}")
            print(f"Address: {result.house_number} {result.street_name}")
            print(f"Borough: {result.borough_name}")
            print(f"BBL: {result.bbl}")
            #print(f"Coordinates: {result.latitude:.6f}, {result.longitude:.6f}")
        except GeoClientError as e:
            print(f"Error: {e}")
        
        # Example 7: Single-Field Search
        print("\n7. Single-Field Search")
        print("-" * 23)
        
        search_queries = [
            "314 west 100 st manhattan",           # Address
            "broadway and west 100 st",            # Intersection
            "empire state building",               # Place
            "1018890001",                          # BBL
            "1079043",                             # BIN
        ]
        
        for query in search_queries:
            try:
                result = client.search(query)
                print(f"\nQuery: '{query}'")
                print(f"Results found: {len(result.results)}")
                
                # Show exact matches
                for search_result in result.results:
                    if search_result.status == "EXACT_MATCH":
                        response = search_result.response
                        '''
                        if "latitude" in response and "longitude" in response:
                            lat = float(response["latitude"])
                            lng = float(response["longitude"])
                            print(f"  Exact match: {lat:.6f}, {lng:.6f}")
                        '''
                        break
                
            except GeoClientError as e:
                print(f"Error searching '{query}': {e}")
        print("example \n8. Get Latitude and Longitude")
        bbl_result = client.bbl("manhattan", "1889", "1")
        print(f"BBL: {bbl_result.bbl}")
        addr_result = client.address(bbl_result.house_number, bbl_result.street_name, bbl_result.borough_name)
        print(f"Address: {addr_result.house_number} {addr_result.street_name}, {addr_result.borough_name}")
        print(f"Coordinates: {addr_result.latitude:.6f}, {addr_result.longitude:.6f}")
        print("\n" + "=" * 50)


        print("✅ Examples completed successfully!")


if __name__ == "__main__":
    main()