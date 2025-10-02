"""
Configuration management for PayMover.

This module provides configuration classes and utilities for managing
API settings, authentication, and other client options.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class PaymoConfig:
    """
    Configuration class for Paymo API client.
    
    This class holds all configuration options for the Paymo API client,
    including authentication, API endpoints, and behavior settings.
    """
    
    # Authentication
    email: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    
    # API Settings
    base_url: str = "https://app.paymoapp.com/api/"
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 0.3
    
    # Rate Limiting
    respect_rate_limits: bool = True
    rate_limit_retry_delay: float = 60.0
    
    # Logging
    log_level: str = "INFO"
    log_requests: bool = False
    log_responses: bool = False
    
    # Request Settings
    default_headers: Dict[str, str] = field(default_factory=dict)
    user_agent: str = "PayMover/1.0.0"
    
    @classmethod
    def from_env(cls) -> 'PaymoConfig':
        """
        Create configuration from environment variables.
        
        Environment variables:
        - PAYMO_EMAIL: Paymo account email
        - PAYMO_PASSWORD: Paymo account password
        - PAYMO_API_KEY: Paymo API key (alternative to email/password)
        - PAYMO_BASE_URL: API base URL
        - PAYMO_TIMEOUT: Request timeout in seconds
        - PAYMO_MAX_RETRIES: Maximum number of retries
        - PAYMO_LOG_LEVEL: Logging level
        - PAYMO_LOG_REQUESTS: Whether to log requests (true/false)
        - PAYMO_LOG_RESPONSES: Whether to log responses (true/false)
        
        Returns:
            PaymoConfig instance with values from environment
        """
        config = cls()
        
        # Authentication
        config.email = os.getenv('PAYMO_EMAIL')
        config.password = os.getenv('PAYMO_PASSWORD')
        config.api_key = os.getenv('PAYMO_API_KEY')
        
        # API Settings
        if os.getenv('PAYMO_BASE_URL'):
            config.base_url = os.getenv('PAYMO_BASE_URL')
        
        if os.getenv('PAYMO_TIMEOUT'):
            try:
                config.timeout = float(os.getenv('PAYMO_TIMEOUT'))
            except ValueError:
                pass
        
        if os.getenv('PAYMO_MAX_RETRIES'):
            try:
                config.max_retries = int(os.getenv('PAYMO_MAX_RETRIES'))
            except ValueError:
                pass
        
        # Logging
        if os.getenv('PAYMO_LOG_LEVEL'):
            config.log_level = os.getenv('PAYMO_LOG_LEVEL')
        
        if os.getenv('PAYMO_LOG_REQUESTS'):
            config.log_requests = os.getenv('PAYMO_LOG_REQUESTS').lower() in ('true', '1', 'yes')
        
        if os.getenv('PAYMO_LOG_RESPONSES'):
            config.log_responses = os.getenv('PAYMO_LOG_RESPONSES').lower() in ('true', '1', 'yes')
        
        return config
    
    @classmethod
    def from_file(cls, filepath: str) -> 'PaymoConfig':
        """
        Create configuration from a JSON file.
        
        Args:
            filepath: Path to the configuration file
            
        Returns:
            PaymoConfig instance with values from file
        """
        import json
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Update config with values from file
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'email': self.email,
            'password': self.password,
            'api_key': self.api_key,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'backoff_factor': self.backoff_factor,
            'respect_rate_limits': self.respect_rate_limits,
            'rate_limit_retry_delay': self.rate_limit_retry_delay,
            'log_level': self.log_level,
            'log_requests': self.log_requests,
            'log_responses': self.log_responses,
            'default_headers': self.default_headers,
            'user_agent': self.user_agent,
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            filepath: Path to save the configuration file
        """
        import json
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.email and not self.api_key:
            raise ValueError("Either email/password or api_key must be provided")
        
        if self.email and not self.password:
            raise ValueError("Password is required when using email authentication")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        
        if self.backoff_factor < 0:
            raise ValueError("Backoff factor must be non-negative")


def get_default_config() -> PaymoConfig:
    """
    Get the default configuration.
    
    This function tries to load configuration from environment variables first,
    then falls back to default values.
    
    Returns:
        PaymoConfig instance
    """
    return PaymoConfig.from_env()
