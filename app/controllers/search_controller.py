from fastapi import Depends, APIRouter

from app.contracts.dtos.search_dtos import SearchRequest, SearchResponse, DeleteEmbeddingsRequest, DeleteEmbeddingsResponse
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.domain.value_objects.search_result import SearchQuery
from app.infrastructure.config.di import get_semantic_search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    service: ISemanticSearchService = Depends(get_semantic_search_service)
) -> SearchResponse:

    query = SearchQuery(
        query_text=request.query,
        limit=request.limit,
        min_score=request.min_score,
        content_types=request.content_types
    )

    return await service.perform_semantic_context(query)


@router.post("/delete-embeddings", response_model=DeleteEmbeddingsResponse)
async def delete_embeddings(
    request: DeleteEmbeddingsRequest,
    service: ISemanticSearchService = Depends(get_semantic_search_service)
) -> DeleteEmbeddingsResponse:

    success = await service.delete_embeddings(request.identifier)

    return DeleteEmbeddingsResponse(
        success=success,
        message="Embeddings deleted successfully" if success else "Failed to delete embeddings"
    )

