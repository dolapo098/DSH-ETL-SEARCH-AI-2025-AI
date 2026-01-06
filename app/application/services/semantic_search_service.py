import logging
from typing import Optional, List

from sqlalchemy import select
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.contracts.providers.i_embedding_provider import IEmbeddingProvider
from app.contracts.repositories.i_vector_store_repository import IVectorStoreRepository
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.contracts.dtos.search_dtos import SearchResponse, SearchResultItem
from app.domain.exceptions.search_exception import (
    EmbeddingGenerationException,
    InvalidSearchQueryException,
    VectorStoreException,
)
from app.domain.value_objects.search_result import SearchQuery, SearchResult
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper
from app.domain.entities.dataset_metadata import DatasetMetadata

logger = logging.getLogger(__name__)


class SemanticSearchService(ISemanticSearchService):

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    MIN_LIMIT = 1
    DEFAULT_MIN_SCORE = 0.0
    MIN_SCORE_THRESHOLD = 0.0
    MAX_SCORE_THRESHOLD = 1.0


    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        vector_store_repository: IVectorStoreRepository,
        repository_wrapper: RepositoryWrapper,
        batch_size: int = 50,
    ):

        self._embedding_provider = embedding_provider
        self._vector_store = vector_store_repository
        self._uow = repository_wrapper
        self._batch_size = batch_size

    async def perform_semantic_context(self, query: SearchQuery) -> SearchResponse:

        try:
            
            if not query.query_text or not query.query_text.strip():
                
                raise InvalidSearchQueryException("Query text cannot be empty")

            query_embedding = await self._embedding_provider.generate_embedding(query.query_text)

            if not query_embedding:
                
                raise EmbeddingGenerationException("Failed to generate embedding for query")

            vector_results = await self._vector_store.search_similar(
                query_embedding, 
                limit=self.DEFAULT_LIMIT, 
                min_score=self.DEFAULT_MIN_SCORE
            )

            if not vector_results:
                
                return SearchResponse(query=query.query_text, results=[], count=0)

            best_chunks: dict[str, SearchResult] = {}

            for result in vector_results:
                existing = best_chunks.get(result.identifier)

                if existing is None or result.score > existing.score:
                    best_chunks[result.identifier] = result

            unique_ids = list(best_chunks.keys())
            
            if not unique_ids:
                metadata_records = []
            else:
                stmt = select(DatasetMetadata).where(DatasetMetadata.file_identifier.in_(unique_ids))
                db_result = await self._uow.dataset_metadata.session.execute(stmt)
                metadata_records = db_result.scalars().all()
            
            title_map = {m.file_identifier: m.title or "Untitled Dataset" for m in metadata_records}

            results = [
                SearchResultItem(
                    identifier=chunk.identifier,
                    title=title_map.get(chunk.identifier, "Untitled Dataset"),
                    description=chunk.text or chunk.description or "",
                    score=chunk.score
                )
                for chunk in sorted(best_chunks.values(), key=lambda c: c.score, reverse=True)
            ]

            return SearchResponse(
                query=query.query_text,
                results=results,
                count=len(results)
            )

        except (InvalidSearchQueryException, EmbeddingGenerationException):
            
            raise
            
        except Exception as e:
            logger.error(f"Error performing semantic context retrieval: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to perform semantic context retrieval: {str(e)}") from e

    async def delete_embeddings(self, identifier: str) -> bool:

        try:
            
            return await self._vector_store.delete_embeddings(identifier)
            
        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to delete embeddings: {str(e)}") from e

    async def ingest_text(
        self, 
        identifier: str, 
        content_type: str, 
        text: str, 
        source_file: Optional[str] = None
    ) -> bool:

        try:
            
            if content_type.lower() == "document":
                
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50,
                    length_function=len,
                )
                chunks = splitter.split_text(text)

                for i in range(0, len(chunks), self._batch_size):
                    batch_chunks = chunks[i : i + self._batch_size]
                    embeddings = await self._embedding_provider.generate_embeddings(batch_chunks)

                    payloads = [
                        {
                            "identifier": identifier,
                            "content_type": content_type,
                            "text": chunk,
                            "source_file": source_file or "unknown",
                            "chunk_index": i + idx,
                            "total_chunks": len(chunks),
                        }
                        for idx, chunk in enumerate(batch_chunks)
                    ]

                    await self._vector_store.index_embeddings_batch(
                        identifier=identifier,
                        content_type=content_type,
                        embeddings=embeddings,
                        payloads=payloads,
                    )

            else:
                embedding = await self._embedding_provider.generate_embedding(text)
                
                await self._vector_store.index_embedding(
                    identifier=identifier,
                    content_type=content_type,
                    text=text,
                    embedding=embedding,
                    metadata={"source_file": source_file or "metadata"}
                )

            return True

        except Exception as e:
            logger.error(f"Error ingesting text: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to ingest text: {str(e)}") from e
