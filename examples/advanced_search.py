"""
Advanced search examples for the GeoClient MOO library.

This script demonstrates the powerful single-field search capabilities,
including natural language parsing and advanced search options.

Before running this script, set your API credentials as environment variables:
    export GEOCLIENT_APP_ID="your_app_id"
    export GEOCLIENT_APP_KEY="your_app_key"
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from geoclient_moo import GeoClient
from geoclient_moo.exceptions import GeoClientError
from dotenv import load_dotenv

# Load .env file - first try current directory, then parent directory
load_dotenv()  # Try current directory first
if not os.getenv("GEOCLIENT_APP_ID"):
    # Try parent directory if not found in current directory
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

def demonstrate_search_types(client: GeoClient) -> None:
    """Demonstrate different types of single-field searches."""
    
    search_examples = [
        # Address searches
        ("314 west 100 st manhattan", "Full address with borough"),
        ("314 w 100 st, ny, ny 10025", "Address with ZIP code"),
        ("314 west 100th street, manhattan", "Address with ordinal street"),
        
        # Intersection searches
        ("broadway and west 100 st", "Simple intersection"),
        ("broadway & w 100 st manhattan", "Intersection with borough"),
        ("5th ave and 42nd st", "Famous intersection"),
        
        # Blockface searches
        ("broadway between west 100 st and west 101 st", "Blockface search"),
        ("amsterdam ave between w 110 st and w 111 st manhattan", "Blockface with borough"),
        
        # Place name searches
        ("empire state building", "Famous landmark"),
        ("central park", "Large area"),
        ("yankee stadium", "Sports venue"),
        ("jfk airport", "Airport"),
        
        # BBL searches (10-digit numbers starting with 1-5)
        ("1018890001", "BBL lookup"),
        ("3012345678", "BBL for Brooklyn"),
        
        # BIN searches (7-digit numbers starting with 1-5) 
        ("1079043", "BIN lookup"),
        ("2000001", "BIN for Bronx"),
    ]
    
    print("🔍 Single-Field Search Examples")
    print("=" * 50)
    
    for query, description in search_examples:
        print(f"\n📍 {description}")
        print(f"Query: '{query}'")
        print("-" * 40)
        
        try:
            result = client.search(query)
            
            print(f"Results found: {len(result.results)}")
            print(f"Exact match: {result.exact_match}")
            
            # Show the best result
            for search_result in result.results:
                if search_result.status in ("EXACT_MATCH", "POSSIBLE_MATCH"):
                    response = search_result.response
                    print(f"Status: {search_result.status}")
                    print(f"Level: {search_result.level}")
                    
                    # Extract key information based on response type
                    if "houseNumber" in response:
                        # Address-type response
                        house_num = response.get("houseNumber", "")
                        street_name = response.get("streetName", "")
                        borough = response.get("boroughName", "")
                        print(f"Address: {house_num} {street_name}, {borough}")
                        
                    elif "crossStreetOne" in response:
                        # Intersection-type response
                        cross1 = response.get("crossStreetOne", "")
                        cross2 = response.get("crossStreetTwo", "")
                        borough = response.get("boroughName", "")
                        print(f"Intersection: {cross1} & {cross2}, {borough}")
                        
                    elif "onStreet" in response:
                        # Blockface-type response
                        on_street = response.get("onStreet", "")
                        cross1 = response.get("crossStreetOne", "")
                        cross2 = response.get("crossStreetTwo", "")
                        print(f"Blockface: {on_street} between {cross1} and {cross2}")
                    
                    # Show coordinates if available
                    if "latitude" in response and "longitude" in response:
                        lat = float(response["latitude"])
                        lng = float(response["longitude"])
                        print(f"Coordinates: {lat:.6f}, {lng:.6f}")
                    
                    break
            
        except GeoClientError as e:
            print(f"❌ Error: {e}")


def demonstrate_advanced_search_options(client: GeoClient) -> None:
    """Demonstrate advanced search options and parameters."""
    
    print("\n\n🔧 Advanced Search Options")
    print("=" * 50)
    
    # Test query that might have similar names
    query = "west 100 street manhattan"  # Slightly different from "west 100 st"
    
    print(f"\nTesting advanced options with: '{query}'")
    print("-" * 50)
    
    # Basic search
    print("\n1. Basic Search:")
    result = client.search(query)
    print(f"   Results: {len(result.results)}")
    print(f"   Exact match: {result.exact_match}")
    
    # Search with tokens returned
    print("\n2. Search with Tokens:")
    result = client.search(query, return_tokens=True)
    print(f"   Results: {len(result.results)}")
    # Note: tokens would be in raw_data if returned by API
    
    # Search with policy information
    print("\n3. Search with Policy Info:")
    result = client.search(query, return_policy=True)
    print(f"   Results: {len(result.results)}")
    
    # Search with rejections
    print("\n4. Search with Rejections:")
    result = client.search(query, return_rejections=True)
    print(f"   Results: {len(result.results)}")
    
    # Search with custom similarity distance
    print("\n5. Search with Higher Similarity Distance:")
    result = client.search(
        "west 100th street manhatan",  # Typo in "manhattan"
        similar_names_distance=12,     # Higher tolerance for typos
        return_rejections=True
    )
    print(f"   Results: {len(result.results)}")
    
    # Search with exact match options
    print("\n6. Search with Exact Match Options:")
    result = client.search(
        query,
        exact_match_for_single_success=True,
        exact_match_max_level=5,
        return_possibles_with_exact=True
    )
    print(f"   Results: {len(result.results)}")
    print(f"   Exact match: {result.exact_match}")


def analyze_search_results(client: GeoClient) -> None:
    """Analyze and categorize different types of search results."""
    
    print("\n\n📊 Search Results Analysis")
    print("=" * 50)
    
    test_queries = [
        "314 west 100 st manhattan",      # Should be exact match
        "314 west 100 street",            # Might need borough disambiguation  
        "broadway and times square",      # Popular intersection
        "invalid address nowhere",        # Should fail
        "empire state",                   # Partial place name
    ]
    
    for query in test_queries:
        print(f"\nAnalyzing: '{query}'")
        print("-" * 30)
        
        try:
            result = client.search(
                query,
                return_rejections=True,
                exact_match_max_level=3
            )
            
            # Categorize results by status
            statuses = {}
            for search_result in result.results:
                status = search_result.status
                if status not in statuses:
                    statuses[status] = 0
                statuses[status] += 1
            
            print(f"Total results: {len(result.results)}")
            print(f"Result statuses:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
            
            # Show level distribution
            levels = [r.level for r in result.results if r.level is not None]
            if levels:
                print(f"Search levels: {min(levels)} to {max(levels)}")
            
        except GeoClientError as e:
            print(f"❌ Error: {e}")


def main():
    """Run all search examples."""
    
    # Get API credentials
    app_id = os.getenv("GEOCLIENT_APP_ID") 
    app_key = os.getenv("GEOCLIENT_APP_KEY")
    
    if not app_id or not app_key:
        print("ERROR: Please set GEOCLIENT_APP_ID and GEOCLIENT_APP_KEY environment variables")
        return
    
    with GeoClient(app_id, app_key) as client:
        # Run all demonstrations
        demonstrate_search_types(client)
        demonstrate_advanced_search_options(client)
        analyze_search_results(client)
        
        print("\n" + "=" * 50)
        print("✅ Advanced search examples completed!")


if __name__ == "__main__":
    main()