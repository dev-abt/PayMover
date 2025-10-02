"""
Unit tests for the Paymo API client.

This module contains comprehensive tests for the main client functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date

from paymover.client import PaymoClient
from paymover.interfaces import HTTPResponse, RateLimitInfo
from paymover.adapters import BasicAuthProvider, DefaultRateLimitHandler
from paymover.exceptions import (
    PaymoAPIError,
    PaymoAuthenticationError,
    PaymoRateLimitError,
    PaymoValidationError,
    PaymoNotFoundError,
    PaymoServerError
)


class TestPaymoClient:
    """Test cases for PaymoClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock()
        self.mock_auth_provider = Mock()
        self.mock_rate_limit_handler = Mock()
        self.mock_logger = Mock()
        
        self.client = PaymoClient(
            http_client=self.mock_http_client,
            auth_provider=self.mock_auth_provider,
            rate_limit_handler=self.mock_rate_limit_handler,
            logger=self.mock_logger,
            base_url="https://api.example.com/",
            default_timeout=30.0
        )
    
    def test_successful_get_request(self):
        """Test successful GET request."""
        # Arrange
        expected_data = {"id": 1, "name": "Test Project"}
        mock_response = HTTPResponse(
            status_code=200,
            headers={},
            data=expected_data,
            url="https://api.example.com/projects/1"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        result = self.client.get("projects/1")
        
        # Assert
        assert result == expected_data
        self.mock_http_client.get.assert_called_once()
        self.mock_rate_limit_handler.update_rate_limit_info.assert_called_once_with(mock_response)
    
    def test_successful_post_request(self):
        """Test successful POST request."""
        # Arrange
        project_data = {"name": "New Project", "description": "Test project"}
        expected_response = {"id": 2, "name": "New Project", "description": "Test project"}
        mock_response = HTTPResponse(
            status_code=201,
            headers={},
            data=expected_response,
            url="https://api.example.com/projects"
        )
        self.mock_http_client.post.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        result = self.client.post("projects", project_data)
        
        # Assert
        assert result == expected_response
        self.mock_http_client.post.assert_called_once()
    
    def test_authentication_error(self):
        """Test authentication error handling."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=401,
            headers={},
            data={"error": "Unauthorized"},
            url="https://api.example.com/projects"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act & Assert
        with pytest.raises(PaymoAuthenticationError) as exc_info:
            self.client.get("projects")
        
        assert "Authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401
    
    def test_not_found_error(self):
        """Test 404 error handling."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=404,
            headers={},
            data={"error": "Not Found"},
            url="https://api.example.com/projects/999"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act & Assert
        with pytest.raises(PaymoNotFoundError) as exc_info:
            self.client.get("projects/999")
        
        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=422,
            headers={},
            data={"error": "Validation failed", "details": ["Name is required"]},
            url="https://api.example.com/projects"
        )
        self.mock_http_client.post.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act & Assert
        with pytest.raises(PaymoValidationError) as exc_info:
            self.client.post("projects", {"description": "No name provided"})
        
        assert "Validation error" in str(exc_info.value)
        assert exc_info.value.status_code == 422
    
    def test_rate_limit_error(self):
        """Test rate limit error handling."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=429,
            headers={"Retry-After": "60"},
            data={"error": "Rate limit exceeded"},
            url="https://api.example.com/projects"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = True
        self.mock_rate_limit_handler.get_retry_delay.return_value = 60.0
        
        # Act & Assert
        with pytest.raises(PaymoRateLimitError) as exc_info:
            self.client.get("projects")
        
        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.retry_after == 60
        assert exc_info.value.status_code == 429
    
    def test_server_error(self):
        """Test server error handling."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=500,
            headers={},
            data={"error": "Internal Server Error"},
            url="https://api.example.com/projects"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act & Assert
        with pytest.raises(PaymoServerError) as exc_info:
            self.client.get("projects")
        
        assert "Server error occurred" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    def test_rate_limit_retry_logic(self):
        """Test rate limit retry logic."""
        # Arrange
        rate_limited_response = HTTPResponse(
            status_code=429,
            headers={"Retry-After": "1"},
            data={"error": "Rate limited"},
            url="https://api.example.com/projects"
        )
        success_response = HTTPResponse(
            status_code=200,
            headers={},
            data=[{"id": 1, "name": "Project 1"}],
            url="https://api.example.com/projects"
        )
        
        self.mock_http_client.get.side_effect = [rate_limited_response, success_response]
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.side_effect = [True, False]
        self.mock_rate_limit_handler.get_retry_delay.return_value = 0.1  # Short delay for testing
        
        # Act
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.client.get("projects")
        
        # Assert
        assert result == [{"id": 1, "name": "Project 1"}]
        assert self.mock_http_client.get.call_count == 2
    
    def test_delete_success(self):
        """Test successful DELETE request."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=204,
            headers={},
            data=None,
            url="https://api.example.com/projects/1"
        )
        self.mock_http_client.delete.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        result = self.client.delete("projects/1")
        
        # Assert
        assert result is True
        self.mock_http_client.delete.assert_called_once()
    
    def test_delete_failure(self):
        """Test DELETE request failure."""
        # Arrange
        mock_response = HTTPResponse(
            status_code=404,
            headers={},
            data={"error": "Not Found"},
            url="https://api.example.com/projects/999"
        )
        self.mock_http_client.delete.return_value = mock_response
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        result = self.client.delete("projects/999")
        
        # Assert
        assert result is False
    
    def test_paginated_get(self):
        """Test paginated GET request."""
        # Arrange
        page1_response = HTTPResponse(
            status_code=200,
            headers={},
            data=[{"id": 1, "name": "Project 1"}, {"id": 2, "name": "Project 2"}],
            url="https://api.example.com/projects?page=1&per_page=2"
        )
        page2_response = HTTPResponse(
            status_code=200,
            headers={},
            data=[{"id": 3, "name": "Project 3"}],
            url="https://api.example.com/projects?page=2&per_page=2"
        )
        page3_response = HTTPResponse(
            status_code=200,
            headers={},
            data=[],
            url="https://api.example.com/projects?page=3&per_page=2"
        )
        
        self.mock_http_client.get.side_effect = [page1_response, page2_response, page3_response]
        self.mock_auth_provider.get_headers.return_value = {}
        self.mock_auth_provider.get_auth_tuple.return_value = None
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        result = self.client.get_paginated("projects", page_size=2)
        
        # Assert
        assert len(result) == 3
        assert result[0]["name"] == "Project 1"
        assert result[1]["name"] == "Project 2"
        assert result[2]["name"] == "Project 3"
        assert self.mock_http_client.get.call_count == 3
    
    def test_headers_inclusion(self):
        """Test that authentication headers are included in requests."""
        # Arrange
        expected_headers = {"Authorization": "Bearer token123"}
        self.mock_auth_provider.get_headers.return_value = expected_headers
        self.mock_auth_provider.get_auth_tuple.return_value = None
        
        mock_response = HTTPResponse(
            status_code=200,
            headers={},
            data={"id": 1, "name": "Test"},
            url="https://api.example.com/projects"
        )
        self.mock_http_client.get.return_value = mock_response
        self.mock_rate_limit_handler.should_retry.return_value = False
        
        # Act
        self.client.get("projects")
        
        # Assert
        call_args = self.mock_http_client.get.call_args
        assert call_args[1]["headers"] == expected_headers
