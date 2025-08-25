"""
Utility functions for the Owlib Python SDK.
"""
import os
import json
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .exceptions import (
    AuthenticationError,
    APIError,
    NetworkError,
    TimeoutError,
    KnowledgeBaseNotFoundError,
    EntryNotFoundError,
    ValidationError
)


class HTTPClient:
    """HTTP client for making requests to the Owlib API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.owlib.ai", timeout: int = 30):
        """
        Initialize the HTTP client.
        
        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'owlib-python-sdk/1.0.0'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: URL query parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            Various Owlib exceptions based on the error type
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            # Prepare request kwargs
            request_kwargs = {
                'timeout': self.timeout,
                'params': params
            }
            
            if data is not None:
                request_kwargs['json'] = data
            
            # Make the request
            response = self.session.request(method, url, **request_kwargs)
            
            # Handle different status codes
            self._handle_response(response)
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                raise APIError(f"Invalid JSON response from API", response.status_code, response.text)
                
        except Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except ConnectionError as e:
            raise NetworkError(f"Network connection error: {str(e)}")
        except RequestException as e:
            raise NetworkError(f"HTTP request failed: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> None:
        """
        Handle HTTP response and raise appropriate exceptions.
        
        Args:
            response: The HTTP response object
            
        Raises:
            Various Owlib exceptions based on the status code
        """
        if response.status_code == 200:
            return
        
        # Try to get error message from response
        error_message = "API request failed"
        try:
            error_data = response.json()
            error_message = error_data.get('error', error_data.get('message', error_message))
        except json.JSONDecodeError:
            error_message = response.text or error_message
        
        # Map status codes to exceptions
        if response.status_code == 401:
            raise AuthenticationError("Invalid or missing API key")
        elif response.status_code == 404:
            # Check if this is a knowledge base or entry not found
            if '/entries/' in response.url:
                raise EntryNotFoundError(f"Entry not found: {error_message}")
            else:
                raise KnowledgeBaseNotFoundError(f"Knowledge base not found: {error_message}")
        elif response.status_code == 400:
            raise ValidationError(f"Invalid request: {error_message}")
        elif response.status_code == 403:
            raise AuthenticationError(f"Access denied: {error_message}")
        elif response.status_code == 429:
            raise APIError(f"Rate limit exceeded: {error_message}", response.status_code, response.text)
        elif response.status_code >= 500:
            raise APIError(f"Server error: {error_message}", response.status_code, response.text)
        else:
            raise APIError(f"API error: {error_message}", response.status_code, response.text)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request('POST', endpoint, data=data)


def get_api_key_from_env() -> Optional[str]:
    """
    Get API key from environment variables.
    
    Returns:
        API key if found, None otherwise
    """
    return os.getenv('OWLIB_API_KEY')


def validate_namespace_name(namespace: str, name: str) -> None:
    """
    Validate namespace and name format.
    
    Args:
        namespace: Knowledge base namespace
        name: Knowledge base name
        
    Raises:
        ValidationError: If format is invalid
    """
    if not namespace or not isinstance(namespace, str):
        raise ValidationError("Namespace must be a non-empty string")
    
    if not name or not isinstance(name, str):
        raise ValidationError("Name must be a non-empty string")
    
    # Basic validation - no spaces, special characters
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    
    if not re.match(pattern, namespace):
        raise ValidationError("Namespace can only contain letters, numbers, underscores, and hyphens")
    
    if not re.match(pattern, name):
        raise ValidationError("Name can only contain letters, numbers, underscores, and hyphens")