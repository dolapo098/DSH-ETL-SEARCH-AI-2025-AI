import hashlib
import logging
from typing import Optional, List

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
)

from app.contracts.repositories.i_vector_store_repository import IVectorStoreRepository
from app.domain.exceptions.search_exception import VectorStoreException
from app.domain.value_objects.search_result import SearchResult

logger = logging.getLogger(__name__)


class QdrantVectorStoreRepository(IVectorStoreRepository):
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "embeddings",
        vector_size: int = 1536,
    ):

        try:
            self._client = AsyncQdrantClient(url=url)
            self._collection = collection_name
            self._vector_size = vector_size
            self._collection_ready = False
            
        except Exception as e:
            logger.error("Failed to initialize Qdrant client", exc_info=True)
            
            raise VectorStoreException(str(e)) from e

    async def _ensure_collection(self):

        if self._collection_ready:
            
            return

        collections = await self._client.get_collections()
        
        if self._collection not in {c.name for c in collections.collections}:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._vector_size,
                    distance=Distance.COSINE,
                ),
            )
            
        self._collection_ready = True

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> List[SearchResult]:

        try:
            await self._ensure_collection()
            
            results = await self._client.search(
                collection_name=self._collection,
                query_vector=query_embedding,
                limit=limit,
                search_params=SearchParams(hnsw_ef=128),
                with_payload=True,
                score_threshold=min_score if min_score > 0 else None,
            )

            return [
                SearchResult(
                    identifier=r.payload.get("identifier"),
                    content_type=r.payload.get("content_type"),
                    text=r.payload.get("text"),
                    score=float(r.score),
                    metadata=r.payload,
                    title=r.payload.get("title"),
                    description=r.payload.get("description")
                )
                for r in results
            ]
            
        except Exception as e:
            logger.error("Error searching Qdrant vectors", exc_info=True)
            
            raise VectorStoreException(str(e)) from e

    async def index_embedding(
        self,
        identifier: str,
        content_type: str,
        text: str,
        embedding: List[float],
        metadata: Optional[dict] = None,
    ) -> bool:

        try:
            await self._ensure_collection()

            payload = {
                "identifier": identifier,
                "content_type": content_type,
                "text": text,
            }
            
            if metadata:
                payload.update(metadata)

            point_id_str = (
                f"{identifier}_{content_type}_{metadata.get('chunk_index')}"
                if metadata and "chunk_index" in metadata
                else f"{identifier}_{content_type}"
            )
            
            point_id = int(hashlib.md5(point_id_str.encode()).hexdigest(), 16) % (2**63)

            await self._client.upsert(
                collection_name=self._collection,
                points=[{"id": point_id, "vector": embedding, "payload": payload}],
            )
            
            return True
            
        except Exception as e:
            logger.error("Error indexing embedding in Qdrant", exc_info=True)
            
            raise VectorStoreException(str(e)) from e

    async def index_embeddings_batch(
        self,
        identifier: str,
        content_type: str,
        embeddings: List[List[float]],
        payloads: List[dict],
    ) -> bool:

        try:
            await self._ensure_collection()

            points = []
            
            for emb, payload in zip(embeddings, payloads):
                point_id_str = (
                    f"{identifier}_{content_type}_{payload.get('chunk_index')}"
                    if "chunk_index" in payload 
                    else f"{identifier}_{content_type}"
                )
                
                point_id = int(hashlib.md5(point_id_str.encode()).hexdigest(), 16) % (2**63)
                points.append({"id": point_id, "vector": emb, "payload": payload})

            await self._client.upsert(collection_name=self._collection, points=points)
            
            return True
            
        except Exception as e:
            logger.error("Error indexing embeddings batch in Qdrant", exc_info=True)
            
            raise VectorStoreException(str(e)) from e

    async def delete_embeddings(self, identifier: str) -> bool:

        try:
            await self._ensure_collection()

            await self._client.delete(
                collection_name=self._collection,
                points_selector=Filter(
                    must=[FieldCondition(key="identifier", match=MatchValue(value=identifier))]
                ),
            )
            
            return True
            
        except Exception as e:
            logger.error("Error deleting embeddings in Qdrant", exc_info=True)
            
            raise VectorStoreException(str(e)) from e

