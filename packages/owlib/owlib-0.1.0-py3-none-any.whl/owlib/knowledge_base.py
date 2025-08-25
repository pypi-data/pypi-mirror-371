"""
KnowledgeBase class for the Owlib Python SDK.
"""
from typing import List, Optional

from .models import Entry, QueryResult
from .utils import HTTPClient, validate_namespace_name
from .exceptions import ValidationError


class KnowledgeBase:
    """
    Represents a knowledge base in the Owlib platform.
    
    This class provides methods to query and fetch entries from a specific knowledge base.
    """
    
    def __init__(self, client: HTTPClient, namespace: str, name: str):
        """
        Initialize a KnowledgeBase instance.
        
        Args:
            client: The HTTP client for API requests
            namespace: The knowledge base namespace
            name: The knowledge base name
        """
        self.client = client
        self.namespace = namespace
        self.name = name
        
        # Validate namespace and name format
        validate_namespace_name(namespace, name)
    
    @property
    def full_name(self) -> str:
        """Get the full name of the knowledge base (namespace/name)."""
        return f"{self.namespace}/{self.name}"
    
    def query(self, query_text: str, top_k: int = 5) -> QueryResult:
        """
        Query the knowledge base for similar entries.
        
        Args:
            query_text: The text to search for
            top_k: Maximum number of results to return (default: 5)
            
        Returns:
            QueryResult containing the matching entries
            
        Raises:
            ValidationError: If input parameters are invalid
            KnowledgeBaseNotFoundError: If the knowledge base doesn't exist
            APIError: If the API request fails
        """
        # Validate input
        if not query_text or not isinstance(query_text, str):
            raise ValidationError("Query text must be a non-empty string")
        
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValidationError("top_k must be a positive integer")
        
        if top_k > 100:  # Reasonable limit
            raise ValidationError("top_k cannot exceed 100")
        
        # Prepare request
        endpoint = f"/api/v1/kb/{self.namespace}/{self.name}/query"
        request_data = {
            "query": query_text,
            "top_k": top_k
        }
        
        # Make API request
        response_data = self.client.post(endpoint, request_data)
        
        # Parse response into data models
        entries = []
        for entry_data in response_data.get('entries', []):
            entry = Entry(
                id=entry_data['id'],
                title=entry_data['title'],
                content=entry_data['content'],
                similarity_score=entry_data.get('similarity_score', 0.0),
                metadata=entry_data.get('metadata', {})
            )
            entries.append(entry)
        
        return QueryResult(
            entries=entries,
            query_text=response_data.get('query_text', query_text),
            total_count=response_data.get('total_count', len(entries))
        )
    
    def fetch(self, entry_id: str) -> Entry:
        """
        Fetch a specific entry by its ID.
        
        Args:
            entry_id: The unique identifier of the entry
            
        Returns:
            The Entry object with complete information
            
        Raises:
            ValidationError: If entry_id is invalid
            EntryNotFoundError: If the entry doesn't exist
            KnowledgeBaseNotFoundError: If the knowledge base doesn't exist
            APIError: If the API request fails
        """
        # Validate input
        if not entry_id or not isinstance(entry_id, str):
            raise ValidationError("Entry ID must be a non-empty string")
        
        # Prepare request
        endpoint = f"/api/v1/kb/{self.namespace}/{self.name}/entries/{entry_id}"
        
        # Make API request
        response_data = self.client.get(endpoint)
        
        # Parse response into Entry model
        return Entry(
            id=response_data['id'],
            title=response_data['title'],
            content=response_data['content'],
            similarity_score=response_data.get('similarity_score', 0.0),
            metadata=response_data.get('metadata', {})
        )
    
    def __str__(self) -> str:
        """Return string representation of the knowledge base."""
        return f"KnowledgeBase({self.full_name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the knowledge base."""
        return f"KnowledgeBase(namespace='{self.namespace}', name='{self.name}')"