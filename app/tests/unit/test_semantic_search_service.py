import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from app.application.services.semantic_search_service import SemanticSearchService
from app.domain.value_objects.search_result import SearchQuery, SearchResult
from app.domain.exceptions.search_exception import (
    EmbeddingGenerationException,
    InvalidSearchQueryException,
    VectorStoreException
)
from app.contracts.providers.i_embedding_provider import IEmbeddingProvider
from app.contracts.repositories.i_vector_store_repository import IVectorStoreRepository
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper
from app.domain.entities.dataset_metadata import DatasetMetadata

class TestSemanticSearchService:

    @pytest.fixture
    def mock_embedding_provider(self):
        provider = Mock(spec=IEmbeddingProvider)
        provider.generate_embedding = AsyncMock()
        provider.generate_embeddings = AsyncMock()
        return provider

    @pytest.fixture
    def mock_vector_store(self):
        store = Mock(spec=IVectorStoreRepository)
        store.search_similar = AsyncMock()
        store.index_embedding = AsyncMock()
        store.index_embeddings_batch = AsyncMock()
        store.delete_embeddings = AsyncMock()
        return store

    @pytest.fixture
    def mock_repository_wrapper(self):
        wrapper = Mock(spec=RepositoryWrapper)
        mock_session = Mock()
        mock_session.execute = AsyncMock()
        wrapper.dataset_metadata = Mock()
        wrapper.dataset_metadata.session = mock_session
        return wrapper

    @pytest.fixture
    def service(self, mock_embedding_provider, mock_vector_store, mock_repository_wrapper):
        return SemanticSearchService(
            embedding_provider=mock_embedding_provider,
            vector_store_repository=mock_vector_store,
            repository_wrapper=mock_repository_wrapper,
            batch_size=2
        )

    @pytest.mark.asyncio
    async def test_perform_semantic_context_returns_results(self, service, mock_embedding_provider, mock_vector_store, mock_repository_wrapper):
        query = SearchQuery(query_text="water quality", limit=10, offset=0)
        mock_embedding_provider.generate_embedding.return_value = [0.1] * 1536
        
        mock_result = SearchResult(identifier="ds-1", score=0.9, title="Water Data", text="Sample content")
        mock_vector_store.search_similar.return_value = [mock_result]
        
        mock_metadata = Mock(spec=DatasetMetadata)
        mock_metadata.file_identifier = "ds-1"
        mock_metadata.title = "Water Data"
        
        mock_db_result = MagicMock()
        mock_db_result.scalars.return_value.all.return_value = [mock_metadata]
        mock_repository_wrapper.dataset_metadata.session.execute.return_value = mock_db_result

        response = await service.perform_semantic_context(query)

        assert response.total_count == 1
        
        assert response.results[0].identifier == "ds-1"
        
        assert response.results[0].title == "Water Data"
        
        mock_embedding_provider.generate_embedding.assert_called_once_with("water quality")

    @pytest.mark.asyncio
    async def test_perform_semantic_context_raises_invalid_query(self, service):
        query = SearchQuery(query_text="", limit=10, offset=0)

        with pytest.raises(InvalidSearchQueryException):
            await service.perform_semantic_context(query)

    @pytest.mark.asyncio
    async def test_ingest_text_metadata_calls_single_index(self, service, mock_embedding_provider, mock_vector_store):
        mock_embedding_provider.generate_embedding.return_value = [0.1] * 1536
        mock_vector_store.index_embedding.return_value = True

        success = await service.ingest_text(identifier="ds-1", content_type="title", text="Test Title")

        assert success is True
        
        mock_embedding_provider.generate_embedding.assert_called_once_with("Test Title")
        
        mock_vector_store.index_embedding.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_text_document_splits_and_batches(self, service, mock_embedding_provider, mock_vector_store):
        long_text = "This is a long sentence that should be split into multiple chunks because it exceeds the chunk size. " * 10
        mock_embedding_provider.generate_embeddings.return_value = [[0.1] * 1536, [0.2] * 1536]
        mock_vector_store.index_embeddings_batch.return_value = True

        success = await service.ingest_text(identifier="ds-1", content_type="document", text=long_text)

        assert success is True
        
        assert mock_embedding_provider.generate_embeddings.call_count >= 1
        
        assert mock_vector_store.index_embeddings_batch.call_count >= 1

    @pytest.mark.asyncio
    async def test_delete_embeddings_calls_store(self, service, mock_vector_store):
        mock_vector_store.delete_embeddings.return_value = True

        success = await service.delete_embeddings("ds-1")

        assert success is True
        
        mock_vector_store.delete_embeddings.assert_called_once_with("ds-1")
