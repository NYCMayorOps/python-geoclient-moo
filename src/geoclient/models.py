"""Data models for GeoClient API responses."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class BaseResponse:
    """Base class for all API responses."""

    raw_data: Dict[str, Any] = field(repr=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseResponse":
        """Create instance from API response dictionary."""
        return cls(raw_data=data)


@dataclass 
class GeosupportInfo:
    """Information about Geosupport processing status."""
    
    return_code: Optional[str] = None
    reason_code: Optional[str] = None
    message: Optional[str] = None
    
    # For Function 1B (address endpoint)
    return_code_1a: Optional[str] = None
    reason_code_1a: Optional[str] = None
    message_1a: Optional[str] = None
    return_code_1e: Optional[str] = None
    reason_code_1e: Optional[str] = None
    message_1e: Optional[str] = None


@dataclass
class AddressResponse(BaseResponse):
    """Response model for address geocoding requests."""
    
    # Basic address information
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    borough_code: Optional[str] = None
    borough_name: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Geographic coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Property information
    bbl: Optional[str] = None
    bin: Optional[str] = None
    building_identification_number: Optional[str] = None
    
    # Administrative areas
    community_district: Optional[str] = None
    census_tract: Optional[str] = None
    neighborhood_tabulation_area: Optional[str] = None
    
    # Cross street information
    cross_street_one: Optional[str] = None
    cross_street_two: Optional[str] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AddressResponse":
        """Create AddressResponse from API response dictionary."""
        # Handle nested response structure - data might be under "address" key
        if "address" in data:
            addr_data = data["address"]
        else:
            addr_data = data
            
        geosupport_info = GeosupportInfo(
            return_code=addr_data.get("geosupportReturnCode"),
            reason_code=addr_data.get("reasonCode"),
            message=addr_data.get("message"),
            return_code_1a=addr_data.get("geosupportReturnCode2"),
            reason_code_1a=addr_data.get("reasonCode2"),
            message_1a=addr_data.get("message2"),
            return_code_1e=addr_data.get("returnCode1e"),
            reason_code_1e=addr_data.get("reasonCode1e"),
        )
        
        return cls(
            raw_data=data,
            house_number=addr_data.get("houseNumber"),
            street_name=addr_data.get("boePreferredStreetName"),
            borough_code=addr_data.get("boroughCode1In"),
            borough_name=addr_data.get("firstBoroughName"),
            zip_code=addr_data.get("zipCode"),
            latitude=_safe_float(addr_data.get("latitude")),
            longitude=_safe_float(addr_data.get("longitude")),
            x_coordinate=_safe_float(addr_data.get("xCoordinate")),
            y_coordinate=_safe_float(addr_data.get("yCoordinate")),
            bbl=addr_data.get("bbl"),
            bin=addr_data.get("buildingIdentificationNumber"),
            building_identification_number=addr_data.get("buildingIdentificationNumber"),
            community_district=addr_data.get("communityDistrict"),
            census_tract=addr_data.get("censusTract2010"),
            neighborhood_tabulation_area=addr_data.get("nta"),
            cross_street_one=addr_data.get("lowCrossStreetName1"),
            cross_street_two=addr_data.get("highCrossStreetName1"),
            geosupport=geosupport_info,
        )


@dataclass
class BBLResponse(BaseResponse):
    """Response model for BBL (Borough-Block-Lot) requests."""
    
    borough_code: Optional[str] = None
    borough_name: Optional[str] = None
    tax_block: Optional[str] = None
    tax_lot: Optional[str] = None
    bbl: Optional[str] = None
    
    # Property information
    building_identification_number: Optional[str] = None
    num_buildings_on_lot: Optional[int] = None
    
    # Address information
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    
    # Geographic coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BBLResponse":
        """Create BBLResponse from API response dictionary."""
        # Handle nested response structure - data is under 'bbl' key
        if "bbl" in data and isinstance(data["bbl"], dict):
            bbl_data = data["bbl"]
        else:
            bbl_data = data
            
        geosupport_info = GeosupportInfo(
            return_code=bbl_data.get("geosupportReturnCode"),
            reason_code=bbl_data.get("reasonCode"),
            message=bbl_data.get("message"),
        )
        
        return cls(
            raw_data=data,
            borough_code=bbl_data.get("bblBoroughCode"),
            borough_name=bbl_data.get("firstBoroughName"),
            tax_block=bbl_data.get("bblTaxBlock"),
            tax_lot=bbl_data.get("bblTaxLot"),
            bbl=bbl_data.get("bbl"),
            building_identification_number=bbl_data.get("buildingIdentificationNumber"),
            num_buildings_on_lot=_safe_int(bbl_data.get("numberOfExistingStructuresOnLot")),
            house_number=bbl_data.get("giLowHouseNumber1"),
            street_name=bbl_data.get("giStreetName1"),
            latitude=_safe_float(bbl_data.get("latitude")),
            longitude=_safe_float(bbl_data.get("longitude")),
            x_coordinate=_safe_float(bbl_data.get("internalLabelXCoordinate")),
            y_coordinate=_safe_float(bbl_data.get("internalLabelYCoordinate")),
            geosupport=geosupport_info,
        )


@dataclass
class BINResponse(BaseResponse):
    """Response model for BIN (Building Identification Number) requests."""
    
    building_identification_number: Optional[str] = None
    bbl: Optional[str] = None
    
    # Address information
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    borough_code: Optional[str] = None
    borough_name: Optional[str] = None
    
    # Geographic coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BINResponse":
        """Create BINResponse from API response dictionary."""
        # Handle nested response structure - data is under 'bin' key
        if "bin" in data and isinstance(data["bin"], dict):
            bin_data = data["bin"]
        else:
            bin_data = data
            
        geosupport_info = GeosupportInfo(
            return_code=bin_data.get("geosupportReturnCode"),
            reason_code=bin_data.get("reasonCode"),
            message=bin_data.get("message"),
        )
        
        return cls(
            raw_data=data,
            building_identification_number=bin_data.get("buildingIdentificationNumber"),
            bbl=bin_data.get("bbl"),
            house_number=bin_data.get("giLowHouseNumber1"),
            street_name=bin_data.get("giStreetName1"),
            borough_code=bin_data.get("bblBoroughCode"),
            borough_name=bin_data.get("firstBoroughName"),
            latitude=_safe_float(bin_data.get("latitude")),
            longitude=_safe_float(bin_data.get("longitude")),
            x_coordinate=_safe_float(bin_data.get("internalLabelXCoordinate")),
            y_coordinate=_safe_float(bin_data.get("internalLabelYCoordinate")),
            geosupport=geosupport_info,
        )


@dataclass
class BlockfaceResponse(BaseResponse):
    """Response model for blockface requests."""
    
    on_street: Optional[str] = None
    cross_street_one: Optional[str] = None
    cross_street_two: Optional[str] = None
    borough_code: Optional[str] = None
    
    # Geographic information
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Street segment information
    segment_length: Optional[float] = None
    street_width: Optional[float] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockfaceResponse":
        """Create BlockfaceResponse from API response dictionary."""
        geosupport_info = GeosupportInfo(
            return_code=data.get("geosupportReturnCode"),
            reason_code=data.get("reasonCode"),
            message=data.get("message"),
        )
        
        return cls(
            raw_data=data,
            on_street=data.get("onStreet"),
            cross_street_one=data.get("crossStreetOne"),
            cross_street_two=data.get("crossStreetTwo"),
            borough_code=data.get("boroughCode"),
            latitude=_safe_float(data.get("latitude")),
            longitude=_safe_float(data.get("longitude")),
            x_coordinate=_safe_float(data.get("xCoordinate")),
            y_coordinate=_safe_float(data.get("yCoordinate")),
            segment_length=_safe_float(data.get("segmentLength")),
            street_width=_safe_float(data.get("streetWidth")),
            geosupport=geosupport_info,
        )


@dataclass
class IntersectionResponse(BaseResponse):
    """Response model for intersection requests."""
    
    cross_street_one: Optional[str] = None
    cross_street_two: Optional[str] = None
    borough_code: Optional[str] = None
    
    # Geographic coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntersectionResponse":
        """Create IntersectionResponse from API response dictionary."""
        geosupport_info = GeosupportInfo(
            return_code=data.get("geosupportReturnCode"),
            reason_code=data.get("reasonCode"),
            message=data.get("message"),
        )
        
        return cls(
            raw_data=data,
            cross_street_one=data.get("crossStreetOne"),
            cross_street_two=data.get("crossStreetTwo"),
            borough_code=data.get("boroughCode"),
            latitude=_safe_float(data.get("latitude")),
            longitude=_safe_float(data.get("longitude")),
            x_coordinate=_safe_float(data.get("xCoordinate")),
            y_coordinate=_safe_float(data.get("yCoordinate")),
            geosupport=geosupport_info,
        )


@dataclass
class PlaceResponse(BaseResponse):
    """Response model for place name requests."""
    
    place_name: Optional[str] = None
    
    # Address information (same as AddressResponse since Place uses Function 1B)
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    borough_code: Optional[str] = None
    borough_name: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Geographic coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    
    # Property information
    bbl: Optional[str] = None
    bin: Optional[str] = None
    
    # Geosupport processing info
    geosupport: GeosupportInfo = field(default_factory=GeosupportInfo)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaceResponse":
        """Create PlaceResponse from API response dictionary."""
        if "place" in data:
            place_data = data["place"]
        else:
            place_data = data

        geosupport_info = GeosupportInfo(
            return_code=place_data.get("geosupportReturnCode"),
            reason_code=place_data.get("reasonCode"),
            message=place_data.get("message"),
            return_code_1a=place_data.get("geosupportReturnCode2"),
            reason_code_1a=place_data.get("reasonCode2"),
            message_1a=place_data.get("message2"),
            return_code_1e=place_data.get("returnCode1e"),
            reason_code_1e=place_data.get("reasonCode1e"),
        )
        
        return cls(
            raw_data=data,
            place_name=place_data.get("boePreferredStreetName"),
            house_number=place_data.get("houseNumber"),
            street_name=place_data.get("streetName"),
            borough_code=place_data.get("boroughCode1In"),
            borough_name=place_data.get("firstBoroughName"),
            zip_code=place_data.get("zipCode"),
            latitude=_safe_float(place_data.get("latitude")),
            longitude=_safe_float(place_data.get("longitude")),
            x_coordinate=_safe_float(place_data.get("xCoordinate")),
            y_coordinate=_safe_float(place_data.get("yCoordinate")),
            bbl=place_data.get("bbl"),
            bin=place_data.get("buildingIdentificationNumber"),
            geosupport=geosupport_info,
        )


@dataclass
class SearchResult:
    """Individual search result from the search endpoint."""
    
    level: Optional[int] = None
    status: Optional[str] = None
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create SearchResult from API response dictionary."""
        return cls(
            level=data.get("level"),
            status=data.get("status"),
            request=data.get("request"),
            response=data.get("response"),
        )


@dataclass
class SearchResponse(BaseResponse):
    """Response model for single-field search requests."""
    
    input: Optional[str] = None
    results: List[SearchResult] = field(default_factory=list)
    
    # Search metadata
    exact_match: Optional[bool] = None
    similar_names: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResponse":
        """Create SearchResponse from API response dictionary."""
        results = []
        if "results" in data:
            for result_data in data["results"]:
                results.append(SearchResult.from_dict(result_data))
        
        return cls(
            raw_data=data,
            input=data.get("input"),
            results=results,
            exact_match=data.get("exactMatch"),
            similar_names=data.get("similarNames", []),
        )


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float, returning None if conversion fails."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int, returning None if conversion fails."""
    if value is None or value == "":
        return None
    try:
        # First try direct int conversion
        return int(value)
    except (ValueError, TypeError):
        try:
            # If that fails, try converting through float first (handles "123.0")
            float_val = float(value)
            if float_val.is_integer():
                return int(float_val)
            else:
                return None  # Not a whole number
        except (ValueError, TypeError):
            return None