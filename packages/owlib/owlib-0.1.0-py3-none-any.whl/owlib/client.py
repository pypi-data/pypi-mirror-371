"""
Main client class for the Owlib Python SDK.
"""
from typing import Optional

from .knowledge_base import KnowledgeBase
from .utils import HTTPClient, get_api_key_from_env
from .exceptions import ValidationError, AuthenticationError


class OwlibClient:
    """
    Main client for interacting with the Owlib AI knowledge platform.
    
    This client handles authentication and provides access to knowledge bases.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.owlib.ai",
        timeout: int = 30
    ):
        """
        Initialize the Owlib client.
        
        Args:
            api_key: API key for authentication. If None, will try to read from 
                    OWLIB_API_KEY environment variable.
            base_url: Base URL for the Owlib API (default: https://api.owlib.ai)
            timeout: Request timeout in seconds (default: 30)
            
        Raises:
            AuthenticationError: If no API key is provided or found
            ValidationError: If parameters are invalid
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = get_api_key_from_env()
        
        if not api_key:
            raise AuthenticationError(
                "No API key provided. Please provide an api_key parameter or set the "
                "OWLIB_API_KEY environment variable."
            )
        
        # Validate parameters
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValidationError("base_url must be a non-empty string")
        
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValidationError("timeout must be a positive integer")
        
        # Initialize HTTP client
        self.http_client = HTTPClient(api_key, base_url, timeout)
        self.base_url = base_url
        self.timeout = timeout
    
    def knowledge_base(self, path: str) -> KnowledgeBase:
        """
        Get a KnowledgeBase instance for the specified path.
        
        Args:
            path: Knowledge base path in format "namespace/name"
            
        Returns:
            KnowledgeBase instance for querying and fetching entries
            
        Raises:
            ValidationError: If the path format is invalid
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Knowledge base path must be a non-empty string")
        
        # Parse namespace/name from path
        parts = path.split('/')
        if len(parts) != 2:
            raise ValidationError(
                "Knowledge base path must be in format 'namespace/name', "
                f"got: '{path}'"
            )
        
        namespace, name = parts
        if not namespace or not name:
            raise ValidationError(
                "Both namespace and name must be non-empty, "
                f"got: namespace='{namespace}', name='{name}'"
            )
        
        return KnowledgeBase(self.http_client, namespace, name)
    
    def __str__(self) -> str:
        """Return string representation of the client."""
        return f"OwlibClient(base_url='{self.base_url}')"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the client."""
        return f"OwlibClient(base_url='{self.base_url}', timeout={self.timeout})"