"""
Main Paymo API client implementation.

This module contains the main client class that orchestrates all API operations.
"""

import time
from typing import Any, Dict, Optional, List

from interfaces import (
    HTTPClient, 
    APIClient, 
    AuthenticationProvider, 
    RateLimitHandler, 
    Logger
)
from adapters import DefaultRateLimitHandler, StandardLogger, RequestsHTTPClient, BasicAuthProvider, APIKeyAuthProvider
from exceptions import (
    PaymoAPIError, 
    PaymoRateLimitError, 
    PaymoAuthenticationError,
    PaymoValidationError,
    PaymoNotFoundError,
    PaymoServerError
)

class PaymoClient(APIClient):
    """
    Main Paymo API client.
    
    This client provides a high-level interface to the Paymo API with
    built-in error handling, rate limiting, and authentication.
    """
    
    def __init__(
        self,
        http_client: HTTPClient,
        auth_provider: AuthenticationProvider,
        rate_limit_handler: Optional[RateLimitHandler] = None,
        logger: Optional[Logger] = None,
        base_url: str = "https://app.paymoapp.com/api/",
        default_timeout: float = 30.0
    ):
        self.http_client = http_client
        self.auth_provider = auth_provider
        self.rate_limit_handler = rate_limit_handler or DefaultRateLimitHandler()
        self.logger = logger or StandardLogger()
        self.base_url = base_url.rstrip('/')
        self.default_timeout = default_timeout
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers.update(self.auth_provider.get_headers())
        return headers
    
    def _handle_response(self, response: Any) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if hasattr(response, 'status_code'):
            status_code = response.status_code
        else:
            status_code = getattr(response, 'status_code', 200)
        
        if 200 <= status_code < 300:
            return response.data if hasattr(response, 'data') else response
        
        # Handle different error cases
        if status_code == 401:
            raise PaymoAuthenticationError(
                "Authentication failed. Please check your credentials.",
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
        elif status_code == 404:
            raise PaymoNotFoundError(
                "Resource not found.",
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
        elif status_code == 422:
            raise PaymoValidationError(
                "Validation error. Please check your request data.",
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
        elif status_code == 429:
            retry_after = None
            if hasattr(response, 'headers'):
                retry_after = response.headers.get("Retry-After")
            raise PaymoRateLimitError(
                "Rate limit exceeded. Please try again later.",
                retry_after=int(retry_after) if retry_after else None,
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
        elif 500 <= status_code < 600:
            raise PaymoServerError(
                f"Server error occurred (HTTP {status_code}).",
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
        else:
            error_message = "Unknown error occurred"
            if hasattr(response, 'data') and isinstance(response.data, dict):
                error_message = response.data.get('message', error_message)
            raise PaymoAPIError(
                error_message,
                status_code=status_code,
                response_data=response.data if hasattr(response, 'data') else {}
            )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Make an API request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        request_timeout = timeout or self.default_timeout
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url}", attempt=attempt)
                
                if method == "GET":
                    response = self.http_client.get(
                        url, headers=headers, params=params, timeout=request_timeout
                    )
                elif method == "POST":
                    response = self.http_client.post(
                        url, json=data, headers=headers, params=params, timeout=request_timeout
                    )
                elif method == "PUT":
                    response = self.http_client.put(
                        url, json=data, headers=headers, params=params, timeout=request_timeout
                    )
                elif method == "DELETE":
                    response = self.http_client.delete(
                        url, headers=headers, params=params, timeout=request_timeout
                    )
                else:
                    raise PaymoAPIError(f"Unsupported HTTP method: {method}")
                
                # Update rate limit info
                self.rate_limit_handler.update_rate_limit_info(response)
                
                # Handle rate limiting
                if self.rate_limit_handler.should_retry(response) and attempt < max_retries:
                    delay = self.rate_limit_handler.get_retry_delay(response)
                    self.logger.warning(f"Rate limited, retrying in {delay} seconds")
                    time.sleep(delay)
                    continue
                
                return self._handle_response(response)
                
            except PaymoRateLimitError as e:
                if attempt < max_retries:
                    delay = e.retry_after or 60.0
                    self.logger.warning(f"Rate limited, retrying in {delay} seconds")
                    time.sleep(delay)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"Request failed, retrying: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
        
        raise PaymoAPIError("Max retries exceeded")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a resource or list of resources."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource."""
        return self._make_request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> bool:
        """Delete a resource."""
        try:
            self._make_request("DELETE", endpoint)
            return True
        except PaymoAPIError:
            return False
    
    def get_paginated(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all results from a paginated endpoint.
        
        This method automatically handles pagination and returns all results.
        """
        all_results = []
        page = 1
        
        while True:
            paginated_params = params or {}
            paginated_params.update({
                'page': page,
                'per_page': page_size
            })
            
            response = self.get(endpoint, params=paginated_params)
            
            # Handle different response formats
            if isinstance(response, list):
                results = response
            elif isinstance(response, dict):
                results = response.get('data', response.get('results', []))
            else:
                break
            
            if not results:
                break
                
            all_results.extend(results)
            
            # Check if we've reached the last page
            if len(results) < page_size:
                break
                
            page += 1
        
        return all_results

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from factory import create_client_with_api_key

    load_dotenv()

    api_key = os.getenv("PAYMO_API_KEY")

    client = create_client_with_api_key(api_key)


    # from pprint import pprint; pprint(client.projects.list(where={'active': True}))

    from pprint import pprint; pprint(client.entries.list(project_id=3438177))