"""
Python Geoclient MOO - A Python wrapper for the NYC OTI Geoclient 2.0 API.

This package provides a clean, Pythonic interface to the NYC Geoclient API,
which is used for geocoding New York City addresses and locations.
"""

from .client import GeoClient
from .exceptions import (
    GeoClientError,
    GeoClientHTTPError,
    GeoClientAuthError,
    GeoClientAPIError,
)
from .models import (
    AddressResponse,
    BBLResponse,
    BINResponse,
    BlockfaceResponse,
    IntersectionResponse,
    PlaceResponse,
    SearchResponse,
)
from .batch_geocode import (
    batch_geocode_addresses,
    geocode_csv,
    load_addresses_from_csv,
    save_results_to_csv,
)

__version__ = "0.1.0"
__author__ = "NYC Mayor's Office of Operations"
__email__ = "gis-development@doitt.nyc.gov"

__all__ = [
    "GeoClient",
    "GeoClientError",
    "GeoClientHTTPError",
    "GeoClientAuthError",
    "GeoClientAPIError",
    "AddressResponse",
    "BBLResponse",
    "BINResponse",
    "BlockfaceResponse",
    "IntersectionResponse",
    "PlaceResponse",
    "SearchResponse",
    "batch_geocode_addresses",
    "geocode_csv",
    "load_addresses_from_csv",
    "save_results_to_csv",
]