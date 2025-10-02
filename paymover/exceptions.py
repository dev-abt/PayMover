"""
Custom exceptions for the Paymo API client.
"""

from typing import Optional, Dict, Any


class PaymoAPIError(Exception):
    """
    Base exception for all Paymo API errors.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class PaymoAuthenticationError(PaymoAPIError):
    """
    Raised when authentication fails.
    """
    pass


class PaymoRateLimitError(PaymoAPIError):
    """
    Raised when rate limit is exceeded.
    """
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class PaymoValidationError(PaymoAPIError):
    """
    Raised when request validation fails.
    """
    pass


class PaymoNotFoundError(PaymoAPIError):
    """
    Raised when a requested resource is not found.
    """
    pass


class PaymoServerError(PaymoAPIError):
    """
    Raised when the Paymo server returns a 5xx error.
    """
    pass
