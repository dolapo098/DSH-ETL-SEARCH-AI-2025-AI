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


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(10, gt=0, le=100)
    min_score: float = Field(0.0, ge=0.0, le=1.0)
    content_types: Optional[List[str]] = None


class DeleteEmbeddingsRequest(BaseModel):
    identifier: str = Field(..., min_length=1)


class DeleteEmbeddingsResponse(BaseModel):
    success: bool
    message: str

