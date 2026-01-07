from typing import List, Optional

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    identifier: str
    title: str
    description: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    count: int
    total_count: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    content_types: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class DeleteEmbeddingsRequest(BaseModel):
    identifier: str = Field(..., min_length=1)


class DeleteEmbeddingsResponse(BaseModel):
    success: bool
    message: str
