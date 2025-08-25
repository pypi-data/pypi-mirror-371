"""
Owlib Python SDK - AI Knowledge Library Platform Client

A Python client library for accessing the Owlib AI knowledge platform.
Query and retrieve structured knowledge from AI-optimized knowledge bases.

Example usage:
    from owlib import OwlibClient
    
    # Initialize client
    client = OwlibClient(api_key="your-api-key")
    
    # Get knowledge base
    kb = client.knowledge_base("history/chinese_ancient")
    
    # Query the knowledge base
    results = kb.query("秦始皇统一六国", top_k=5)
    
    # Process results
    for entry in results.entries:
        print(f"Title: {entry.title}")
        print(f"Similarity: {entry.similarity_score:.2f}")
        print(f"Content: {entry.content[:200]}...")
"""

from .client import OwlibClient
from .knowledge_base import KnowledgeBase
from .models import Entry, QueryResult
from .exceptions import (
    OwlibError,
    AuthenticationError,
    KnowledgeBaseNotFoundError,
    EntryNotFoundError,
    APIError,
    NetworkError,
    TimeoutError,
    ValidationError
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Owlib Team"
__email__ = "support@owlib.ai"
__description__ = "Python SDK for the Owlib AI Knowledge Platform"

# Public API
__all__ = [
    # Main classes
    "OwlibClient",
    "KnowledgeBase",
    # Data models
    "Entry", 
    "QueryResult",
    # Exceptions
    "OwlibError",
    "AuthenticationError",
    "KnowledgeBaseNotFoundError", 
    "EntryNotFoundError",
    "APIError",
    "NetworkError",
    "TimeoutError",
    "ValidationError",
    # Metadata
    "__version__"
]