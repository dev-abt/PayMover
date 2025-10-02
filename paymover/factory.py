"""
Factory functions for creating Paymo API clients.

This module provides convenient factory functions for creating
configured Paymo API clients with sensible defaults.
"""

from typing import Optional, Dict, Any

from client import PaymoClient
from adapters import (
    RequestsHTTPClient, 
    BasicAuthProvider, 
    APIKeyAuthProvider,
    DefaultRateLimitHandler,
    StandardLogger
)
from endpoints import ProjectsEndpoint, ClientsEndpoint, TasksEndpoint, TimeEntriesEndpoint


def create_client(
    email: str,
    password: str,
    base_url: str = "https://app.paymoapp.com/api/",
    timeout: float = 30.0,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    logger: Optional[Any] = None
) -> PaymoClient:
    """
    Create a Paymo API client with basic authentication.
    
    This is the most common way to create a client for the Paymo API.
    
    Args:
        email: Your Paymo account email
        password: Your Paymo account password
        base_url: Base URL for the API (defaults to Paymo's API)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
        backoff_factor: Backoff factor for retry delays
        logger: Optional logger instance
        
    Returns:
        Configured PaymoClient instance
        
    Example:
        >>> client = create_client("user@example.com", "password")
        >>> projects = client.projects.list()
    """
    # Create HTTP client
    http_client = RequestsHTTPClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor
    )
    
    # Create auth provider
    auth_provider = BasicAuthProvider(email, password)
    
    # Create rate limit handler
    rate_limit_handler = DefaultRateLimitHandler()
    
    # Create logger
    if logger is None:
        logger = StandardLogger()
    
    # Create main client
    client = PaymoClient(
        http_client=http_client,
        auth_provider=auth_provider,
        rate_limit_handler=rate_limit_handler,
        logger=logger,
        base_url=base_url,
        default_timeout=timeout
    )
    
    # Add endpoint interfaces
    client.projects = ProjectsEndpoint(client)
    client.clients = ClientsEndpoint(client)
    client.tasks = TasksEndpoint(client)
    client.time_entries = TimeEntriesEndpoint(client)
    
    return client


def create_client_with_api_key(
    api_key: str,
    base_url: str = "https://app.paymoapp.com/api/",
    timeout: float = 30.0,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    logger: Optional[Any] = None
) -> PaymoClient:
    """
    Create a Paymo API client with API key authentication.
    
    This method can be used if Paymo supports API key authentication.
    
    Args:
        api_key: Your Paymo API key
        base_url: Base URL for the API (defaults to Paymo's API)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
        backoff_factor: Backoff factor for retry delays
        logger: Optional logger instance
        
    Returns:
        Configured PaymoClient instance
    """
    # Create HTTP client
    http_client = RequestsHTTPClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
        backoff_factor=backoff_factor
    )
    
    # Create auth provider
    auth_provider = APIKeyAuthProvider(api_key)
    
    # Create rate limit handler
    rate_limit_handler = DefaultRateLimitHandler()
    
    # Create logger
    if logger is None:
        logger = StandardLogger()
    
    # Create main client
    client = PaymoClient(
        http_client=http_client,
        auth_provider=auth_provider,
        rate_limit_handler=rate_limit_handler,
        logger=logger,
        base_url=base_url,
        default_timeout=timeout
    )
    
    # Add endpoint interfaces
    client.projects = ProjectsEndpoint(client)
    client.clients = ClientsEndpoint(client)
    client.tasks = TasksEndpoint(client)
    client.time_entries = TimeEntriesEndpoint(client)
    
    return client


def create_custom_client(
    http_client: Any,
    auth_provider: Any,
    rate_limit_handler: Optional[Any] = None,
    logger: Optional[Any] = None,
    base_url: str = "https://app.paymoapp.com/api/",
    default_timeout: float = 30.0
) -> PaymoClient:
    """
    Create a Paymo API client with custom components.
    
    This method allows for maximum flexibility by allowing you to provide
    your own implementations of the various components.
    
    Args:
        http_client: Custom HTTP client implementation
        auth_provider: Custom authentication provider
        rate_limit_handler: Custom rate limit handler (optional)
        logger: Custom logger (optional)
        base_url: Base URL for the API
        default_timeout: Default request timeout
        
    Returns:
        Configured PaymoClient instance
    """
    # Create main client
    client = PaymoClient(
        http_client=http_client,
        auth_provider=auth_provider,
        rate_limit_handler=rate_limit_handler,
        logger=logger,
        base_url=base_url,
        default_timeout=default_timeout
    )
    
    # Add endpoint interfaces
    client.projects = ProjectsEndpoint(client)
    client.clients = ClientsEndpoint(client)
    client.tasks = TasksEndpoint(client)
    client.time_entries = TimeEntriesEndpoint(client)
    
    return client
