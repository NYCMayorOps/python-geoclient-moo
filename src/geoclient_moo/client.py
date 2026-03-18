"""Main GeoClient class for interacting with the NYC Geoclient v2 API."""

import os
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests

from .exceptions import (
    GeoClientAPIError,
    GeoClientAuthError,
    GeoClientError,
    GeoClientHTTPError,
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


class GeoClient:
    """
    Python client for the NYC Geoclient v2 API.
    
    This client provides methods to geocode NYC addresses, BBLs, BINs, 
    intersections, blockfaces, places, and perform single-field searches.
    
    Args:
        subscription_key: Your Geoclient API subscription key (primary or
            secondary). If not provided, reads from the GEOCLIENT_SUBSCRIPTION_KEY
            environment variable.
        base_url: Base URL for the Geoclient API (defaults to production)
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retries for failed requests (default: 3)
        retry_delay: Delay between retries in seconds (default: 1.0)
    
    Example:
        >>> client = GeoClient("your_subscription_key")
        >>> result = client.address("314", "west 100 st", "manhattan")
        >>> print(result.latitude, result.longitude)
    """
    
    DEFAULT_BASE_URL = "https://api.nyc.gov/geoclient/v2/"
    ENV_VAR = "GEOCLIENT_SUBSCRIPTION_KEY"
    
    def __init__(
        self,
        subscription_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.subscription_key = subscription_key or os.environ.get(self.ENV_VAR, "")
        if not self.subscription_key:
            raise ValueError(
                "subscription_key is required. Pass it directly or set the "
                f"{self.ENV_VAR} environment variable."
            )
            
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        # Validate base_url format
        if not (self.base_url.startswith('http://') or self.base_url.startswith('https://')):
            raise ValueError(
                f"Invalid base_url '{self.base_url}'. Must start with http:// or https://. "
                f"Did you mean to pass this as subscription_key instead?"
            )
            
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        
        # Ensure base URL ends with a slash
        if not self.base_url.endswith("/"):
            self.base_url += "/"
            
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "python-geoclient-moo/0.1.0",
            "Accept": "application/json",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        })
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any],
        response_class: type,
    ) -> Union[AddressResponse, BBLResponse, BINResponse, BlockfaceResponse, 
               IntersectionResponse, PlaceResponse, SearchResponse]:
        """
        Make an HTTP request to the Geoclient API with retries and error handling.
        
        Args:
            endpoint: API endpoint (e.g., "address.json")
            params: Query parameters for the request
            response_class: Response model class to use for parsing
            
        Returns:
            Parsed response object
            
        Raises:
            GeoClientError: For various API and HTTP errors
        """
        params = params.copy()

        # Build URL
        url = urljoin(self.base_url, endpoint)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )
                
                # Handle HTTP errors
                if response.status_code == 401:
                    raise GeoClientAuthError(
                        f"Authentication failed (401) for {url}: {response.text}",
                        status_code=401,
                        response_text=response.text,
                    )
                elif response.status_code == 403:
                    raise GeoClientAuthError(
                        f"Access forbidden (403) for {url}: {response.text}",
                        status_code=403,
                        response_text=response.text,
                    )
                elif response.status_code == 400:
                    raise GeoClientHTTPError(
                        f"Bad request. Check your parameters. {response.text}",
                        status_code=400,
                        response_text=response.text,
                    )
                elif response.status_code == 404:
                    raise GeoClientHTTPError(
                        f"Endpoint not found: {url}",
                        status_code=404,
                        response_text=response.text,
                    )
                elif response.status_code >= 500:
                    # Server errors - retry these
                    if attempt < self.retries:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise GeoClientHTTPError(
                        f"Server error (HTTP {response.status_code}): {response.text}",
                        status_code=response.status_code,
                        response_text=response.text,
                    )
                elif not response.ok:
                    raise GeoClientHTTPError(
                        f"HTTP error {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_text=response.text,
                    )
                
                # Parse JSON response
                try:
                    data = response.json()
                except ValueError as e:
                    raise GeoClientError(f"Invalid JSON response: {e}")
                
                # Check for Geosupport errors
                self._check_geosupport_errors(data)
                
                # Create and return response object
                return response_class.from_dict(data)
                
            except (requests.exceptions.RequestException, GeoClientError) as e:
                last_exception = e
                if attempt < self.retries and not isinstance(e, (GeoClientAuthError, GeoClientAPIError)):
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    break
        
        # If we get here, all retries failed
        if isinstance(last_exception, GeoClientError):
            raise last_exception
        else:
            raise GeoClientError(f"Request failed after {self.retries + 1} attempts: {last_exception}")
    
    def _check_geosupport_errors(self, data: Dict[str, Any]) -> None:
        """
        Check for Geosupport API errors in the response data.
        
        Args:
            data: Response data from API
            
        Raises:
            GeoClientAPIError: If Geosupport returned an error code
        """
        # The API wraps response data under a nested key (e.g. "address", "bbl")
        check_data = data
        if "geosupportReturnCode" not in data:
            for value in data.values():
                if isinstance(value, dict) and "geosupportReturnCode" in value:
                    check_data = value
                    break

        # Check main return code
        return_code = check_data.get("geosupportReturnCode")
        if return_code and return_code not in ("00", "01"):
            reason_code = check_data.get("reasonCode")
            message = check_data.get("message", "Geosupport error")
            raise GeoClientAPIError(
                f"Geosupport error (code {return_code}): {message}",
                geosupport_return_code=return_code,
                reason_code=reason_code,
                details=data,
            )
        
        # For Function 1B (address/place), check both sub-function codes
        return_code_1a = check_data.get("geosupportReturnCode2")
        return_code_1e = check_data.get("returnCode1e")
        
        if return_code_1a and return_code_1a not in ("00", "01"):
            reason_code = check_data.get("reasonCode2")
            message = check_data.get("message2", "Geosupport error in Function 1A")
            raise GeoClientAPIError(
                f"Geosupport Function 1A error (code {return_code_1a}): {message}",
                geosupport_return_code=return_code_1a,
                reason_code=reason_code,
                details=data,
            )
        
        if return_code_1e and return_code_1e not in ("00", "01"):
            reason_code = check_data.get("reasonCode1e")
            message = "Geosupport error in Function 1E"
            raise GeoClientAPIError(
                f"Geosupport Function 1E error (code {return_code_1e}): {message}",
                geosupport_return_code=return_code_1e,
                reason_code=reason_code,
                details=data,
            )
    
    def _validate_borough(self, borough: str) -> str:
        """
        Validate and normalize borough parameter.
        
        Args:
            borough: Borough name or code
            
        Returns:
            Normalized borough name
            
        Raises:
            ValueError: If borough is invalid
        """
        borough_mapping = {
            "manhattan": "Manhattan",
            "bronx": "Bronx", 
            "brooklyn": "Brooklyn",
            "queens": "Queens",
            "staten island": "Staten Island",
            "si": "Staten Island",
            "1": "Manhattan",
            "2": "Bronx",
            "3": "Brooklyn", 
            "4": "Queens",
            "5": "Staten Island",
        }
        
        normalized = borough_mapping.get(borough.lower())
        if not normalized:
            valid_values = list(set(borough_mapping.values()))
            raise ValueError(f"Invalid borough '{borough}'. Valid values: {valid_values}")
        
        return normalized
    
    def address(
        self,
        house_number: str,
        street: str,
        borough: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> AddressResponse:
        """
        Geocode a NYC address.
        
        Args:
            house_number: House number of the address
            street: Street name or 7-digit street code
            borough: Borough name (required if zip not given)
            zip_code: 5-digit ZIP code (required if borough not given)
            
        Returns:
            AddressResponse with geocoding results
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.address("314", "west 100 st", "manhattan")
            >>> print(f"Coordinates: {result.latitude}, {result.longitude}")
        """
        if not house_number or not street:
            raise ValueError("house_number and street are required")
        
        if not borough and not zip_code:
            raise ValueError("Either borough or zip_code must be provided")
        
        params = {
            "houseNumber": house_number,
            "street": street,
        }
        
        if borough:
            params["borough"] = self._validate_borough(borough)
        if zip_code:
            params["zip"] = zip_code
            
        return self._make_request("address", params, AddressResponse)
    
    def bbl(self, borough: str, block: str, lot: str) -> BBLResponse:
        """
        Get property information by Borough-Block-Lot (BBL).
        
        Args:
            borough: Borough name or code
            block: Tax block number
            lot: Tax lot number
            
        Returns:
            BBLResponse with property information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.bbl("manhattan", "1889", "1")
            >>> print(f"Address: {result.house_number} {result.street_name}")
        """
        if not all([borough, block, lot]):
            raise ValueError("borough, block, and lot are required")
        
        params = {
            "borough": self._validate_borough(borough),
            "block": block,
            "lot": lot,
        }
        
        return self._make_request("bbl", params, BBLResponse)
    
    def bin_(self, bin_number: str) -> BINResponse:
        """
        Get property information by Building Identification Number (BIN).
        
        Args:
            bin_number: Building identification number
            
        Returns:
            BINResponse with building information
            
        Raises:
            ValueError: If BIN is missing
            GeoClientError: For API errors
            
        Example:
            >>> result = client.bin_("1079043")
            >>> print(f"Address: {result.house_number} {result.street_name}")
        """
        if not bin_number:
            raise ValueError("bin_number is required")
        
        params = {"bin": bin_number}
        
        return self._make_request("bin", params, BINResponse)
    
    def blockface(
        self,
        on_street: str,
        cross_street_one: str,
        cross_street_two: str,
        borough: str,
        borough_cross_street_one: Optional[str] = None,
        borough_cross_street_two: Optional[str] = None,
        compass_direction: Optional[str] = None,
    ) -> BlockfaceResponse:
        """
        Get blockface information between two cross streets.
        
        Args:
            on_street: Street name of target blockface
            cross_street_one: First cross street
            cross_street_two: Second cross street  
            borough: Borough of on_street
            borough_cross_street_one: Borough of first cross street (optional)
            borough_cross_street_two: Borough of second cross street (optional)
            compass_direction: Side of street (N, S, E, W) (optional)
            
        Returns:
            BlockfaceResponse with blockface information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.blockface(
            ...     "amsterdam ave", "w 110 st", "w 111 st", "manhattan"
            ... )
            >>> print(f"Segment length: {result.segment_length}")
        """
        if not all([on_street, cross_street_one, cross_street_two, borough]):
            raise ValueError("on_street, cross_street_one, cross_street_two, and borough are required")
        
        if compass_direction and compass_direction.upper() not in ("N", "S", "E", "W"):
            raise ValueError("compass_direction must be one of: N, S, E, W")
        
        params = {
            "onStreet": on_street,
            "crossStreetOne": cross_street_one,
            "crossStreetTwo": cross_street_two,
            "borough": self._validate_borough(borough),
        }
        
        if borough_cross_street_one:
            params["boroughCrossStreetOne"] = self._validate_borough(borough_cross_street_one)
        if borough_cross_street_two:
            params["boroughCrossStreetTwo"] = self._validate_borough(borough_cross_street_two)
        if compass_direction:
            params["compassDirection"] = compass_direction.upper()
            
        return self._make_request("blockface", params, BlockfaceResponse)
    
    def intersection(
        self,
        cross_street_one: str,
        cross_street_two: str,
        borough: str,
        borough_cross_street_two: Optional[str] = None,
        compass_direction: Optional[str] = None,
    ) -> IntersectionResponse:
        """
        Get intersection information for two cross streets.
        
        Args:
            cross_street_one: First cross street
            cross_street_two: Second cross street
            borough: Borough of first cross street or both if no other borough provided
            borough_cross_street_two: Borough of second cross street (optional)
            compass_direction: Required for streets that intersect more than once (N, S, E, W)
            
        Returns:
            IntersectionResponse with intersection information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.intersection("broadway", "w 99 st", "manhattan")
            >>> print(f"Intersection at: {result.latitude}, {result.longitude}")
        """
        if not all([cross_street_one, cross_street_two, borough]):
            raise ValueError("cross_street_one, cross_street_two, and borough are required")
        
        if compass_direction and compass_direction.upper() not in ("N", "S", "E", "W"):
            raise ValueError("compass_direction must be one of: N, S, E, W")
        
        params = {
            "crossStreetOne": cross_street_one,
            "crossStreetTwo": cross_street_two,
            "borough": self._validate_borough(borough),
        }
        
        if borough_cross_street_two:
            params["boroughCrossStreetTwo"] = self._validate_borough(borough_cross_street_two)
        if compass_direction:
            params["compassDirection"] = compass_direction.upper()
            
        return self._make_request("intersection", params, IntersectionResponse)
    
    def place(
        self,
        name: str,
        borough: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> PlaceResponse:
        """
        Geocode a well-known NYC place name.
        
        Args:
            name: Place name of well-known NYC location
            borough: Borough name (required if zip not given)
            zip_code: 5-digit ZIP code (required if borough not given)
            
        Returns:
            PlaceResponse with place information
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.place("empire state building", "manhattan")
            >>> print(f"Location: {result.latitude}, {result.longitude}")
        """
        if not name:
            raise ValueError("name is required")
        
        if not borough and not zip_code:
            raise ValueError("Either borough or zip_code must be provided")
        
        params = {"name": name}
        
        if borough:
            params["borough"] = self._validate_borough(borough)
        if zip_code:
            params["zip"] = zip_code
            
        return self._make_request("place", params, PlaceResponse)
    
    def search(
        self,
        input_text: str,
        exact_match_for_single_success: Optional[bool] = None,
        exact_match_max_level: Optional[int] = None,
        return_policy: Optional[bool] = None,
        return_possibles_with_exact: Optional[bool] = None,
        return_rejections: Optional[bool] = None,
        return_tokens: Optional[bool] = None,
        similar_names_distance: Optional[int] = None,
    ) -> SearchResponse:
        """
        Perform single-field search with natural language parsing.
        
        This endpoint can recognize and parse various input formats including:
        - Addresses: "314 west 100 st manhattan"
        - Intersections: "broadway and w 100 st"  
        - BBLs: "1000670001"
        - BINs: "1079043"
        - Blockfaces: "broadway between w 100 st and w 101 st"
        - Places: "empire state building"
        
        Args:
            input_text: Unparsed location input
            exact_match_for_single_success: Consider single success as exact match
            exact_match_max_level: Maximum sub-search levels (default: 3, max: 6)
            return_policy: Return search policy information
            return_possibles_with_exact: Return possible matches with exact match
            return_rejections: Return rejected response data
            return_tokens: Return parsed input tokens
            similar_names_distance: Max Levenshtein distance for similar names (default: 8)
            
        Returns:
            SearchResponse with search results
            
        Raises:
            ValueError: If input is missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.search("314 west 100 st manhattan")
            >>> for search_result in result.results:
            ...     if search_result.status == "EXACT_MATCH":
            ...         print(f"Found: {search_result.response}")
        """
        if not input_text:
            raise ValueError("input_text is required")
        
        params = {"input": input_text}
        
        if exact_match_for_single_success is not None:
            params["exactMatchForSingleSuccess"] = str(exact_match_for_single_success).lower()
        if exact_match_max_level is not None:
            if not 0 <= exact_match_max_level <= 6:
                raise ValueError("exact_match_max_level must be between 0 and 6")
            params["exactMatchMaxLevel"] = exact_match_max_level
        if return_policy is not None:
            params["returnPolicy"] = str(return_policy).lower()
        if return_possibles_with_exact is not None:
            params["returnPossiblesWithExact"] = str(return_possibles_with_exact).lower()
        if return_rejections is not None:
            params["returnRejections"] = str(return_rejections).lower()
        if return_tokens is not None:
            params["returnTokens"] = str(return_tokens).lower()
        if similar_names_distance is not None:
            if similar_names_distance < 0:
                raise ValueError("similar_names_distance must be non-negative")
            params["similarNamesDistance"] = similar_names_distance
            
        return self._make_request("search", params, SearchResponse)
    
    def get_cross_streets_from_address(
        self,
        house_number: str,
        street: str,
        borough: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> AddressResponse:
        """
        Get cross streets for a NYC address.
        
        This method geocodes the address and returns cross street information
        along with other address details.
        
        Args:
            house_number: House number of the address
            street: Street name or 7-digit street code
            borough: Borough name (required if zip not given)
            zip_code: 5-digit ZIP code (required if borough not given)
            
        Returns:
            AddressResponse with cross street information included
            
        Raises:
            ValueError: If required parameters are missing or invalid
            GeoClientError: For API errors
            
        Example:
            >>> result = client.get_cross_streets_from_address("253", "broadway", "manhattan")
            >>> print(f"Cross streets: {result.cross_street_one} and {result.cross_street_two}")
        """
        if not house_number or not street:
            raise ValueError("house_number and street are required")
        
        if not borough and not zip_code:
            raise ValueError("Either borough or zip_code must be provided")
        
        params = {
            "houseNumber": house_number,
            "street": street,
        }
        
        if borough:
            params["borough"] = self._validate_borough(borough)
        if zip_code:
            params["zip"] = zip_code
            
        return self._make_request("address", params, AddressResponse)
    
    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()
    
    def __enter__(self) -> "GeoClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()