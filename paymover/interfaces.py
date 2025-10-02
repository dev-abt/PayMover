"""
Core interfaces for the Paymo API client.

This module defines the abstract interfaces that all implementations must follow,
enabling dependency injection and easy testing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods supported by the API."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

@dataclass
class HTTPResponse:
    """Represents an HTTP response."""
    status_code: int
    headers: Dict[str, str]
    data: Any
    url: str


@dataclass
class RateLimitInfo:
    """Information about API rate limits."""
    limit: int
    remaining: int
    decay_period: int
    retry_after: Optional[int] = None


class HTTPClient(ABC):
    """
    Abstract interface for HTTP clients.
    
    This interface allows for different HTTP implementations (requests, httpx, etc.)
    while maintaining a consistent API.
    """
    
    @abstractmethod
    def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a GET request."""
        pass
    
    @abstractmethod
    def post(
        self, 
        url: str, 
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a POST request."""
        pass
    
    @abstractmethod
    def put(
        self, 
        url: str, 
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a PUT request."""
        pass
    
    @abstractmethod
    def delete(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make a DELETE request."""
        pass


class AuthenticationProvider(ABC):
    """
    Abstract interface for authentication providers.
    
    This allows for different authentication methods (basic auth, API keys, OAuth, etc.).
    """
    
    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        pass
    
    @abstractmethod
    def get_auth_tuple(self) -> Optional[tuple]:
        """Get authentication tuple for basic auth (username, password)."""
        pass


class APIClient(ABC):
    """
    Abstract interface for API clients.
    
    This defines the contract that all API client implementations must follow.
    """
    
    @abstractmethod
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a resource or list of resources."""
        pass
    
    @abstractmethod
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        pass
    
    @abstractmethod
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource."""
        pass
    
    @abstractmethod
    def delete(self, endpoint: str) -> bool:
        """Delete a resource."""
        pass


class RateLimitHandler(ABC):
    """
    Abstract interface for rate limit handling.
    
    This allows for different strategies to handle rate limiting.
    """
    
    @abstractmethod
    def should_retry(self, response: HTTPResponse) -> bool:
        """Determine if a request should be retried due to rate limiting."""
        pass
    
    @abstractmethod
    def get_retry_delay(self, response: HTTPResponse) -> float:
        """Get the delay before retrying a rate-limited request."""
        pass
    
    @abstractmethod
    def update_rate_limit_info(self, response: HTTPResponse) -> None:
        """Update internal rate limit tracking."""
        pass


class Logger(ABC):
    """
    Abstract interface for logging.
    
    This allows for different logging implementations.
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        pass
