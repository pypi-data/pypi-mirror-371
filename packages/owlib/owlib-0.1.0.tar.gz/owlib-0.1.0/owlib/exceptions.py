"""
Custom exceptions for the Owlib Python SDK.
"""


class OwlibError(Exception):
    """Base exception class for all Owlib-related errors."""
    pass


class AuthenticationError(OwlibError):
    """Raised when API authentication fails."""
    pass


class KnowledgeBaseNotFoundError(OwlibError):
    """Raised when the requested knowledge base does not exist."""
    pass


class EntryNotFoundError(OwlibError):
    """Raised when the requested entry does not exist."""
    pass


class APIError(OwlibError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class NetworkError(OwlibError):
    """Raised when network-related errors occur."""
    pass


class TimeoutError(OwlibError):
    """Raised when API requests time out."""
    pass


class ValidationError(OwlibError):
    """Raised when input validation fails."""
    pass