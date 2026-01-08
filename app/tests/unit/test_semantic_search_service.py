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

class TestData:
    """Centralized test data for SemanticSearchService tests."""
    IDENTIFIER_1 = "ds-1"
    IDENTIFIER_2 = "ds-2"
    QUERY_TEXT = "water quality"
    EMBEDDING = [0.1] * 1536
    
    @staticmethod
    def create_mock_result(identifier: str, score: float, title: str = "Test Title"):
        return SearchResult(
            identifier=identifier,
            score=score,
            title=title,
            text=f"Sample content for {identifier}"
        )

    @staticmethod
    def create_mock_metadata(identifier: str, title: str):
        metadata = Mock(spec=DatasetMetadata)
        metadata.file_identifier = identifier
        metadata.title = title
        return metadata

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
    async def test_perform_semantic_context_with_threshold_filtering(self, service, mock_embedding_provider, mock_vector_store, mock_repository_wrapper):
        # Arrange: User requests a strict threshold of 0.85
        query = SearchQuery(query_text=TestData.QUERY_TEXT, limit=10, offset=0, min_score=0.85)
        mock_embedding_provider.generate_embedding.return_value = TestData.EMBEDDING
        
        # Store returns two results: one passes (0.9), one fails (0.6)
        # Note: Qdrant usually handles score_threshold, but we test that the service passes it correctly
        res1 = TestData.create_mock_result(TestData.IDENTIFIER_1, 0.9, "Passes")
        mock_vector_store.search_similar.return_value = [res1]
        
        mock_metadata = TestData.create_mock_metadata(TestData.IDENTIFIER_1, "Passes")
        mock_db_result = MagicMock()
        mock_db_result.scalars.return_value.all.return_value = [mock_metadata]
        mock_repository_wrapper.dataset_metadata.session.execute.return_value = mock_db_result

        # Act
        response = await service.perform_semantic_context(query)

        # Assert
        assert response.total_count == 1
        assert response.results[0].identifier == TestData.IDENTIFIER_1
        # Verify the service passed the custom min_score to the repository
        mock_vector_store.search_similar.assert_called_once_with(
            TestData.EMBEDDING,
            limit=service.DEFAULT_LIMIT,
            min_score=0.85
        )

    @pytest.mark.asyncio
    async def test_perform_semantic_context_uses_default_threshold_if_none_provided(self, service, mock_embedding_provider, mock_vector_store, mock_repository_wrapper):
        # Arrange: No min_score provided in query
        query = SearchQuery(query_text=TestData.QUERY_TEXT, limit=10, offset=0)
        mock_embedding_provider.generate_embedding.return_value = TestData.EMBEDDING
        mock_vector_store.search_similar.return_value = []

        # Act
        await service.perform_semantic_context(query)

        # Assert: Should use DEFAULT_MIN_SCORE (0.65)
        mock_vector_store.search_similar.assert_called_once_with(
            TestData.EMBEDDING,
            limit=service.DEFAULT_LIMIT,
            min_score=service.DEFAULT_MIN_SCORE
        )

    @pytest.mark.asyncio
    async def test_perform_semantic_context_returns_empty_when_no_results_meet_threshold(self, service, mock_embedding_provider, mock_vector_store):
        # Arrange
        query = SearchQuery(query_text="random noise", min_score=0.95)
        mock_embedding_provider.generate_embedding.return_value = TestData.EMBEDDING
        mock_vector_store.search_similar.return_value = [] # Qdrant filtered everything out

        # Act
        response = await service.perform_semantic_context(query)

        # Assert
        assert response.total_count == 0
        assert len(response.results) == 0

    @pytest.mark.asyncio
    async def test_ingest_text_metadata_calls_single_index(self, service, mock_embedding_provider, mock_vector_store):
        mock_embedding_provider.generate_embedding.return_value = TestData.EMBEDDING
        mock_vector_store.index_embedding.return_value = True

        success = await service.ingest_text(identifier=TestData.IDENTIFIER_1, content_type="title", text="Test Title")

        assert success is True
        mock_embedding_provider.generate_embedding.assert_called_once_with("Test Title")
        mock_vector_store.index_embedding.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_text_document_splits_and_batches(self, service, mock_embedding_provider, mock_vector_store):
        long_text = "This is a long sentence that should be split into multiple chunks because it exceeds the chunk size. " * 10
        mock_embedding_provider.generate_embeddings.return_value = [TestData.EMBEDDING, TestData.EMBEDDING]
        mock_vector_store.index_embeddings_batch.return_value = True

        success = await service.ingest_text(identifier=TestData.IDENTIFIER_1, content_type="document", text=long_text)

        assert success is True
        assert mock_embedding_provider.generate_embeddings.call_count >= 1
        assert mock_vector_store.index_embeddings_batch.call_count >= 1

    @pytest.mark.asyncio
    async def test_delete_embeddings_calls_store(self, service, mock_vector_store):
        mock_vector_store.delete_embeddings.return_value = True

        success = await service.delete_embeddings(TestData.IDENTIFIER_1)

        assert success is True
        mock_vector_store.delete_embeddings.assert_called_once_with(TestData.IDENTIFIER_1)
