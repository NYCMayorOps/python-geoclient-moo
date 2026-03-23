
import csv
import dataclasses
import time
from typing import Dict, List
from geoclient import GeoClient
from geoclient.exceptions import GeoClientError
from geoclient.models import BatchGeocodeResult


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
                'house_number': normalized.get('house_number') or None,
                'street': normalized['street'],
                'borough': normalized['borough'],
            })
    return addresses


def batch_geocode_addresses(addresses: List[Dict[str, str]], client: GeoClient, delay: float = 0.1) -> List[BatchGeocodeResult]:
    """
    Geocode a batch of addresses with error handling and rate limiting.

    Args:
        addresses: List of address dictionaries with keys: house_number, street, borough
        client: Initialized GeoClient instance
        delay: Delay between requests in seconds (for rate limiting)

    Returns:
        List of BatchGeocodeResult with success/error information for each address
    """
    results = []

    for i, addr in enumerate(addresses, 1):
        house_number_display = addr['house_number'] or '(no house number)'
        print(f"Processing {i}/{len(addresses)}: {house_number_display} {addr['street']}, {addr['borough']}")

        if not addr['house_number']:
            try:
                geocoded = client.place(addr['street'], addr['borough'])
                results.append(BatchGeocodeResult.from_place_response(
                    addr['street'], addr['borough'], geocoded
                ))
            except GeoClientError as e:
                results.append(BatchGeocodeResult(
                    input_house_number=addr['house_number'],
                    input_street=addr['street'],
                    input_borough=addr['borough'],
                    error_message=str(e),
                    geosupport_return_code=getattr(e, 'geosupport_return_code', None),
                ))
                print(f"  \u274c Error (place fallback): {e}")

            if delay > 0:
                time.sleep(delay)
            continue

        try:
            geocoded = client.address(addr['house_number'], addr['street'], addr['borough'])
            results.append(BatchGeocodeResult.from_address_response(
                addr['house_number'], addr['street'], addr['borough'], geocoded
            ))
        except GeoClientError as e:
            results.append(BatchGeocodeResult(
                input_house_number=addr['house_number'],
                input_street=addr['street'],
                input_borough=addr['borough'],
                error_message=str(e),
                geosupport_return_code=getattr(e, 'geosupport_return_code', None),
            ))
            print(f"  ❌ Error: {e}")

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

    successful = sum(1 for r in results if r.success)
    print(f"Done: {successful}/{len(results)} geocoded successfully → {output_file}")


def save_results_to_csv(results: List[BatchGeocodeResult], filename: str) -> None:
    """Save geocoding results to a CSV file."""
    if not results:
        print("No results to save")
        return

    rows = [dataclasses.asdict(r) for r in results]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Results saved to {filename}")

