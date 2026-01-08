from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class SearchResult:
    identifier: str
    score: float
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    text: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class SearchQuery:
    query_text: str
    content_types: Optional[List[str]] = field(default_factory=list)
    limit: int = 10
    offset: int = 0
    min_score: Optional[float] = None
