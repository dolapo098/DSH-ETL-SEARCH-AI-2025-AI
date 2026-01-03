from typing import Protocol


class IEmbeddingService(Protocol):
    """
    Interface for the embedding service responsible for processing dataset metadata and generating vector embeddings.
    """

    async def process_dataset_heavy_lifting(self, dataset_metadata_id: int) -> bool:
        """
        Processes a dataset by metadata ID, generating embeddings for its title, abstract, and supporting documents.

        Args:
            dataset_metadata_id (int): The unique identifier of the dataset metadata to process.

        Returns:
            bool: True if processing was successful, False otherwise.
        """
        ...

