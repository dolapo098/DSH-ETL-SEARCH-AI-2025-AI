import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.repositories.qdrant_vectore_store_repository import QdrantVectorStoreRepository
from app.domain.exceptions.search_exception import VectorStoreException

class TestQdrantVectorStoreRepository:

    @pytest.fixture
    def mock_qdrant_client(self):
        with patch("app.infrastructure.repositories.qdrant_vectore_store_repository.AsyncQdrantClient") as mock:
            client = mock.return_value

            client.get_collections = AsyncMock()
            client.create_collection = AsyncMock()
            client.query_points = AsyncMock()
            client.upsert = AsyncMock()
            client.delete = AsyncMock()

            yield client

    @pytest.fixture
    def repository(self, mock_qdrant_client):
        return QdrantVectorStoreRepository(
            url="http://localhost:6333",
            collection_name="test_collection",
            vector_size=1536
        )

    @pytest.mark.asyncio
    async def test_ensure_collection_creates_when_missing(self, repository, mock_qdrant_client):
        mock_qdrant_client.get_collections.return_value = MagicMock(collections=[])

        await repository._ensure_collection()

        mock_qdrant_client.create_collection.assert_called_once()
        
        assert repository._collection_ready is True

    @pytest.mark.asyncio
    async def test_ensure_collection_skips_when_exists(self, repository, mock_qdrant_client):
        existing_collection = MagicMock()
        existing_collection.name = "test_collection"
        mock_qdrant_client.get_collections.return_value = MagicMock(collections=[existing_collection])

        await repository._ensure_collection()

        mock_qdrant_client.create_collection.assert_not_called()
        
        assert repository._collection_ready is True

    @pytest.mark.asyncio
    async def test_search_similar_returns_mapped_results(self, repository, mock_qdrant_client):
        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.85
        mock_point.payload = {
            "identifier": "test-ds",
            "title": "Test Title",
            "text": "Sample content"
        }

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_response

        results = await repository.search_similar(query_embedding=[0.1] * 1536)

        assert len(results) == 1
        
        assert results[0].identifier == "test-ds"
        
        assert results[0].score == 0.85

    @pytest.mark.asyncio
    async def test_index_embedding_calls_upsert_with_payload(self, repository, mock_qdrant_client):
        success = await repository.index_embedding(
            identifier="ds-123",
            content_type="document",
            text="Content to index",
            embedding=[0.2] * 1536
        )

        assert success is True

        mock_qdrant_client.upsert.assert_called_once()
        
        args, kwargs = mock_qdrant_client.upsert.call_args
        
        assert kwargs["points"][0]["payload"]["identifier"] == "ds-123"

    @pytest.mark.asyncio
    async def test_delete_embeddings_uses_correct_filter(self, repository, mock_qdrant_client):
        success = await repository.delete_embeddings(identifier="ds-123")

        assert success is True

        mock_qdrant_client.delete.assert_called_once()
        
        args, kwargs = mock_qdrant_client.delete.call_args
        
        assert "identifier" in str(kwargs["points_selector"])

    @pytest.mark.asyncio
    async def test_search_similar_raises_vector_store_exception_on_client_error(self, repository, mock_qdrant_client):
        mock_qdrant_client.query_points.side_effect = Exception("Connection error")

        with pytest.raises(VectorStoreException) as excinfo:
            await repository.search_similar(query_embedding=[0.1] * 1536)

        assert "Connection error" in str(excinfo.value)
