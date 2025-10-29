"""Custom exceptions for the GeoClient MOO library."""

from typing import Any, Dict, Optional


class GeoClientError(Exception):
    """Base exception class for all GeoClient errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GeoClientHTTPError(GeoClientError):
    """Exception raised for HTTP-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_text: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.response_text = response_text


class GeoClientAuthError(GeoClientHTTPError):
    """Exception raised for authentication/authorization errors (401, 403)."""

    pass


class GeoClientAPIError(GeoClientError):
    """Exception raised for Geosupport API-level errors."""

    def __init__(
        self,
        message: str,
        geosupport_return_code: Optional[str] = None,
        reason_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.geosupport_return_code = geosupport_return_code
        self.reason_code = reason_code