"""
PayMover - Python API client for Paymo project management service.

This package provides a clean, type-safe interface to the Paymo API
using the adapter pattern for maximum flexibility and testability.
"""

from .client import PaymoClient
from .interfaces import HTTPClient, APIClient
from .adapters import RequestsHTTPClient
from .exceptions import PaymoAPIError, PaymoRateLimitError, PaymoAuthenticationError

__version__ = "1.0.0"
__author__ = "PayMover Team"

__all__ = [
    "PaymoClient",
    "HTTPClient",
    "APIClient", 
    "RequestsHTTPClient",
    "PaymoAPIError",
    "PaymoRateLimitError",
    "PaymoAuthenticationError",
]
