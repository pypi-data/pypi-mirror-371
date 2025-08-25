"""
Data models for the Owlib Python SDK.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Entry:
    """Knowledge entry from Owlib knowledge base."""
    id: str
    title: str
    content: str
    similarity_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata as empty dict if None."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QueryResult:
    """Result from querying a knowledge base."""
    entries: List[Entry]
    query_text: str
    total_count: int
    
    def __len__(self) -> int:
        """Return the number of entries in the result."""
        return len(self.entries)
    
    def __iter__(self):
        """Allow iteration over entries."""
        return iter(self.entries)
    
    def __getitem__(self, index):
        """Allow indexing into entries."""
        return self.entries[index]