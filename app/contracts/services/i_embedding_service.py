from typing import List, Protocol


class IEmbeddingService(Protocol):
    """
    Interface for the embedding service responsible for processing dataset metadata and generating vector representations.
    """

    async def process_dataset_heavy_lifting(self, dataset_metadata_id: int) -> bool:
        """
        Processes a dataset by metadata ID, generating embeddings for its title, abstract, and supporting documents.

        Args:
            dataset_metadata_id (int): The unique identifier of the dataset metadata to process.

        Returns:
            bool: True if processing was successful.
        """
        ...

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a single string.

        Args:
            text (str): Input text.

        Returns:
            List[float]: Vector representation.
        """
        ...

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of strings in batch.

        Args:
            texts (List[str]): List of input texts.

        Returns:
            List[List[float]]: List of vector representations.
        """
        ...
