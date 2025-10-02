"""
Concrete implementations of the abstract interfaces.

This module contains the actual implementations that can be used in production.
"""

from typing import Any, Dict, Optional
from urllib.parse import urljoin
import base64

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from interfaces import (
    HTTPClient, 
    HTTPResponse, 
    AuthenticationProvider, 
    RateLimitHandler,
    Logger
)
from exceptions import PaymoAPIError


class RequestsHTTPClient(HTTPClient):
    """
    HTTP client implementation using the requests library.
    
    This is the default HTTP client implementation that uses the popular
    requests library for making HTTP calls.
    """
    
    def __init__(
        self, 
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        """Make an HTTP request and return a standardized response."""
        full_url = urljoin(self.base_url, url)
        request_timeout = timeout or self.timeout
        
        try:
            response = self.session.request(
                method=method,
                url=full_url,
                data=data,
                json=json,
                headers=headers,
                params=params,
                timeout=request_timeout
            )
            
            # Parse response data
            try:
                response_data = response.json()
            except (ValueError, json.JSONDecodeError):
                response_data = response.text
            
            return HTTPResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=response_data,
                url=response.url
            )
            
        except requests.exceptions.RequestException as e:
            raise PaymoAPIError(f"Request failed: {str(e)}")
    
    def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        return self._make_request("GET", url, headers=headers, params=params, timeout=timeout)
    
    def post(
        self, 
        url: str, 
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        return self._make_request("POST", url, data=data, json=json, headers=headers, params=params, timeout=timeout)
    
    def put(
        self, 
        url: str, 
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        return self._make_request("PUT", url, data=data, json=json, headers=headers, params=params, timeout=timeout)
    
    def delete(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> HTTPResponse:
        return self._make_request("DELETE", url, headers=headers, params=params, timeout=timeout)


class BasicAuthProvider(AuthenticationProvider):
    """
    Basic authentication provider using email and password.
    
    This is the standard authentication method for the Paymo API.
    """
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
    
    def get_headers(self) -> Dict[str, str]:
        """Basic auth doesn't require custom headers."""
        return {}
    
    def get_auth_tuple(self) -> tuple:
        """Return the email and password for basic auth."""
        return (self.email, self.password)


class APIKeyAuthProvider(AuthenticationProvider):
    """
    API key authentication provider.
    
    This can be used if Paymo supports API key authentication.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_headers(self) -> Dict[str, str]:
        """Return headers with API key."""
        credentials = f"{self.api_key}:x"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    def get_auth_tuple(self) -> Optional[tuple]:
        """API key auth doesn't use basic auth tuple."""
        return None


class DefaultRateLimitHandler(RateLimitHandler):
    """
    Default rate limit handler implementation.
    
    This implementation follows the standard rate limiting headers
    provided by the Paymo API.
    """
    
    def __init__(self):
        self.rate_limit_info = None
    
    def should_retry(self, response: HTTPResponse) -> bool:
        """Check if the response indicates rate limiting."""
        return response.status_code == 429
    
    def get_retry_delay(self, response: HTTPResponse) -> float:
        """Get the retry delay from response headers."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            return float(retry_after)
        return 60.0  # Default 1 minute delay
    
    def update_rate_limit_info(self, response: HTTPResponse) -> None:
        """Update rate limit information from response headers."""
        from interfaces import RateLimitInfo
        
        limit = response.headers.get("X-Ratelimit-Limit")
        remaining = response.headers.get("X-Ratelimit-Remaining")
        decay_period = response.headers.get("X-Ratelimit-Decay-Period")
        
        if all([limit, remaining, decay_period]):
            self.rate_limit_info = RateLimitInfo(
                limit=int(limit),
                remaining=int(remaining),
                decay_period=int(decay_period)
            )


class StandardLogger(Logger):
    """
    Standard logging implementation using Python's logging module.
    """
    
    def __init__(self, name: str = "paymover"):
        import logging
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        self.logger.error(message, extra=kwargs)
