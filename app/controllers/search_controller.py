from app.contracts.dtos.search_dtos import SearchRequest, SearchResponse, DeleteEmbeddingsRequest, DeleteEmbeddingsResponse
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.domain.value_objects.search_result import SearchQuery


class SearchController:
    """
    Controller handling semantic search operations.
    """

    async def semantic_search(
        self,
        request: SearchRequest,
        service: ISemanticSearchService
    ) -> SearchResponse:

        query = SearchQuery(
            query_text=request.query,
            content_types=request.content_types,
            limit=request.limit,
            offset=request.offset
        )

        return await service.perform_semantic_context(query)

    async def delete_embeddings(
        self,
        request: DeleteEmbeddingsRequest,
        service: ISemanticSearchService
    ) -> DeleteEmbeddingsResponse:

        success = await service.delete_embeddings(request.identifier)

        return DeleteEmbeddingsResponse(
            success=success,
            message="Embeddings deleted successfully" if success else "Failed to delete embeddings"
        )
