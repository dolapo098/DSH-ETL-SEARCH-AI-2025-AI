from typing import Protocol


class IEmbeddingProvider(Protocol):
    """
    Interface for generating numerical vector representations of text.
    """

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generates a vector embedding for a single text string.

        Args:
            text (str): The input text.

        Returns:
            list[float]: The generated embedding vector.
        """
        ...

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generates vector embeddings for a list of text strings.

        Args:
            texts (list[str]): The list of input texts.

        Returns:
            list[list[float]]: A list of generated embedding vectors.
        """
        ...

