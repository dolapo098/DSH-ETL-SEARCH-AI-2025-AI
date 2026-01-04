import logging
import chromadb
from chromadb.config import Settings
from typing import List, Optional, Any

from app.contracts.repositories.i_vector_store_repository import IVectorStoreRepository
from app.domain.exceptions.search_exception import VectorStoreException
from app.domain.value_objects.search_result import SearchResult

logger = logging.getLogger(__name__)


class ChromaVectorStoreRepository(IVectorStoreRepository):
    def __init__(self, persist_directory: Optional[str] = None, collection_name: str = "embeddings"):

        try:
            
            if persist_directory:
                self._client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
                
            else:
                self._client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False)
                )

            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma client: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to initialize Chroma vector store: {str(e)}") from e

    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 10, 
        min_score: float = 0.0
    ) -> List[SearchResult]:

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
            )

            search_results = []
            
            if results["ids"] and len(results["ids"]) > 0:
                ids = results["ids"][0]
                documents = results["documents"][0] if results["documents"] else []
                metadatas = results["metadatas"][0] if results["metadatas"] else []
                distances = results["distances"][0] if results["distances"] else []

                for i, (doc_id, doc_text, metadata, distance) in enumerate(
                    zip(ids, documents, metadatas, distances)
                ):
                    similarity = max(0.0, min(1.0, 1.0 - distance))

                    if similarity >= min_score:
                        identifier = metadata.get("identifier", doc_id) if metadata else doc_id
                        content_type = metadata.get("content_type", "document") if metadata else "document"

                        search_results.append(
                            SearchResult(
                                identifier=identifier,
                                content_type=content_type,
                                text=doc_text,
                                score=float(similarity),
                                metadata=metadata,
                                title=metadata.get("title") if metadata else None,
                                description=metadata.get("description") if metadata else None
                            )
                        )

            return search_results

        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to search similar vectors: {str(e)}") from e

    async def index_embedding(
        self, 
        identifier: str, 
        content_type: str, 
        text: str, 
        embedding: List[float], 
        metadata: Optional[dict] = None
    ) -> bool:

        try:
            
            if metadata and "chunk_index" in metadata:
                doc_id = f"{identifier}_{content_type}_{metadata.get('source_file', 'unknown')}_{metadata['chunk_index']}"
                
            else:
                doc_id = f"{identifier}_{content_type}"
            
            entry_metadata = {"identifier": identifier, "content_type": content_type}
            
            if metadata:
                entry_metadata.update(metadata)
            
            self._collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[entry_metadata],
            )
            
            return True

        except Exception as e:
            logger.error(f"Error indexing embedding: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to index embedding: {str(e)}") from e

    async def index_embeddings_batch(
        self,
        identifier: str,
        content_type: str,
        embeddings: List[List[float]],
        payloads: List[dict]
    ) -> bool:

        try:
            ids = []
            
            for payload in payloads:
                
                if "chunk_index" in payload:
                    doc_id = f"{identifier}_{content_type}_{payload.get('source_file', 'unknown')}_{payload['chunk_index']}"
                    
                else:
                    doc_id = f"{identifier}_{content_type}"
                    
                ids.append(doc_id)

            documents = [p.get("text", "") for p in payloads]
            
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=payloads,
            )
            
            return True

        except Exception as e:
            logger.error(f"Error batch indexing embeddings: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to batch index embeddings: {str(e)}") from e

    async def delete_embeddings(self, identifier: str) -> bool:

        try:
            results = self._collection.get(
                where={"identifier": {"$eq": identifier}}
            )

            if not results["ids"]:
                
                return True

            self._collection.delete(ids=results["ids"])
            
            return True

        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}", exc_info=True)
            
            raise VectorStoreException(f"Failed to delete embeddings: {str(e)}") from e

