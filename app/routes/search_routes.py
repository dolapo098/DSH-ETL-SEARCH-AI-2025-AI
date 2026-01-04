from fastapi import APIRouter, Depends

from app.controllers.search_controller import SearchController
from app.contracts.dtos.search_dtos import SearchRequest, SearchResponse, DeleteEmbeddingsRequest, DeleteEmbeddingsResponse
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.infrastructure.di import get_semantic_search_service

router = APIRouter(prefix="/search", tags=["Search"])
controller = SearchController()


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    service: ISemanticSearchService = Depends(get_semantic_search_service)
) -> SearchResponse:

    return await controller.semantic_search(request, service)


@router.post("/delete-embeddings", response_model=DeleteEmbeddingsResponse)
async def delete_embeddings(
    request: DeleteEmbeddingsRequest,
    service: ISemanticSearchService = Depends(get_semantic_search_service)
) -> DeleteEmbeddingsResponse:

    return await controller.delete_embeddings(request, service)

