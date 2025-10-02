"""
Pytest configuration and fixtures for PayMover tests.

This module provides common fixtures and configuration for all tests.
"""

import pytest
from unittest.mock import Mock
from paymover.interfaces import HTTPResponse


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response."""
    return HTTPResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        data={"id": 1, "name": "Test"},
        url="https://api.example.com/test"
    )


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    client = Mock()
    client.get.return_value = HTTPResponse(
        status_code=200,
        headers={},
        data={"id": 1, "name": "Test"},
        url="https://api.example.com/test"
    )
    return client


@pytest.fixture
def mock_auth_provider():
    """Create a mock authentication provider."""
    provider = Mock()
    provider.get_headers.return_value = {"Authorization": "Bearer token"}
    provider.get_auth_tuple.return_value = None
    return provider


@pytest.fixture
def mock_rate_limit_handler():
    """Create a mock rate limit handler."""
    handler = Mock()
    handler.should_retry.return_value = False
    handler.get_retry_delay.return_value = 60.0
    return handler


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    return logger
