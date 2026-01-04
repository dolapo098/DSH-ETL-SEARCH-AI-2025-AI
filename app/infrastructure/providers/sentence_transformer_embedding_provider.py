import asyncio
from typing import List
from sentence_transformers import SentenceTransformer

from app.contracts.providers.i_embedding_provider import IEmbeddingProvider


class SentenceTransformerEmbeddingProvider(IEmbeddingProvider):
    def __init__(self, model: SentenceTransformer):
        self._model = model

    async def generate_embedding(self, text: str) -> List[float]:

        def _encode() -> List[float]:
            
            return self._model.encode(
                text, 
                convert_to_numpy=True, 
                show_progress_bar=False
            ).tolist()

        return await asyncio.to_thread(_encode)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:

        def _encode_batch() -> List[List[float]]:
            
            return self._model.encode(
                texts, 
                convert_to_numpy=True, 
                show_progress_bar=False
            ).tolist()

        return await asyncio.to_thread(_encode_batch)

