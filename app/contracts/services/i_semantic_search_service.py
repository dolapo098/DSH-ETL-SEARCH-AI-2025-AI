from typing import List, Protocol, Optional

from app.contracts.dtos.search_dtos import SearchResponse
from app.domain.value_objects.search_result import SearchQuery


class ISemanticSearchService(Protocol):
    """
    Interface for semantic search services providing high-level search and ingestion capabilities.
    """

    async def perform_semantic_context(self, query: SearchQuery) -> SearchResponse:
        """
        Performs a semantic search based on the provided query.

        Args:
            query (SearchQuery): The search query parameters.

        Returns:
            SearchResponse: The search results and metadata.
        """
        ...

    async def delete_embeddings(self, identifier: str) -> bool:
        """
        Deletes all vector embeddings associated with a specific identifier.

        Args:
            identifier (str): The identifier to remove.

        Returns:
            bool: True if deletion was successful.
        """
        ...

    async def ingest_text(
        self, 
        identifier: str, 
        content_type: str, 
        text: str, 
        source_file: Optional[str] = None
    ) -> bool:
        """
        Ingests text into the semantic search system, splitting into chunks if necessary.

        Args:
            identifier (str): Unique identifier for the source.
            content_type (str): Type of content being ingested.
            text (str): The raw text content.
            source_file (Optional[str]): The path to the source file if applicable.

        Returns:
            bool: True if ingestion was successful.
        """
        ...
