from typing import List, Protocol, Optional

from app.domain.value_objects.search_result import SearchResult


class IVectorStoreRepository(Protocol):
    """
    Interface for vector store repositories responsible for indexing and searching embeddings.
    """

    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 10, 
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Searches for vectors similar to the query embedding.

        Args:
            query_embedding (List[float]): The vector representation of the query.
            limit (int): Maximum number of results to return.
            min_score (float): Minimum similarity score threshold.

        Returns:
            List[SearchResult]: A list of matching search results.
        """
        ...

    async def index_embedding(
        self, 
        identifier: str, 
        content_type: str, 
        text: str, 
        embedding: List[float], 
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Indexes a single embedding in the vector store.

        Args:
            identifier (str): Unique identifier for the document/dataset.
            content_type (str): Type of content (e.g., 'title', 'description').
            text (str): The raw text content.
            embedding (List[float]): The vector representation.
            metadata (Optional[dict]): Additional metadata to store.

        Returns:
            bool: True if indexing was successful.
        """
        ...

    async def index_embeddings_batch(
        self,
        identifier: str,
        content_type: str,
        embeddings: List[List[float]],
        payloads: List[dict]
    ) -> bool:
        """
        Indexes a batch of embeddings in the vector store.

        Args:
            identifier (str): Unique identifier for the document/dataset.
            content_type (str): Type of content.
            embeddings (List[List[float]]): List of vector representations.
            payloads (List[dict]): List of metadata payloads corresponding to each embedding.

        Returns:
            bool: True if batch indexing was successful.
        """
        ...

    async def delete_embeddings(self, identifier: str) -> bool:
        """
        Deletes all embeddings associated with an identifier.

        Args:
            identifier (str): The identifier to remove.

        Returns:
            bool: True if deletion was successful.
        """
        ...
