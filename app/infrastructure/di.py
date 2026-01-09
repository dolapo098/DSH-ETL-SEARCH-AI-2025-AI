import os
from functools import lru_cache
from fastapi import Depends
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.discovery_agent_service import DiscoveryAgentService
from app.application.services.embedding_service import EmbeddingService
from app.application.services.semantic_search_service import SemanticSearchService
from app.contracts.providers.i_embedding_provider import IEmbeddingProvider
from app.contracts.providers.i_llm_provider import ILLMProvider
from app.contracts.services.i_discovery_agent_service import IDiscoveryAgentService
from app.contracts.services.i_embedding_service import IEmbeddingService
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper
from app.infrastructure.data_access.session import AsyncSessionLocal
from app.infrastructure.parsers.rocrate_parser import ROCrateParser
from app.infrastructure.providers.pdf_document_extractor import PdfDocumentExtractor
from app.infrastructure.providers.rtf_document_extractor import RtfDocumentExtractor
from app.infrastructure.providers.sentence_transformer_embedding_provider import SentenceTransformerEmbeddingProvider
from app.infrastructure.providers.word_document_extractor import WordDocumentExtractor
from app.infrastructure.providers.zip_downloader import ZipDownloader
from app.infrastructure.repositories.qdrant_vectore_store_repository import QdrantVectorStoreRepository


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    """
    Returns the singleton instance of the sentence transformer model.
    """

    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embedding_provider() -> IEmbeddingProvider:
    """
    Returns the implementation of the embedding provider.
    """

    return SentenceTransformerEmbeddingProvider(get_embedding_model())


def get_llm_provider() -> ILLMProvider:
    """
    Returns the LLM provider for both intent extraction and answer synthesis.
    Uses Factory Pattern with dictionary registry. Defaults to Google Gemini.
    """

    from app.infrastructure.factories.llm_provider_factory import LLMProviderFactory
    
    return LLMProviderFactory.create()


def get_vector_store_repository() -> QdrantVectorStoreRepository:
    """
    Returns the implementation of the vector store repository.
    """

    return QdrantVectorStoreRepository(
        url="http://localhost:6333",
        collection_name="embeddings",
        vector_size=384
    )


async def get_session():
    """
    Provides an async database session.
    """

    async with AsyncSessionLocal() as session:
        
        yield session


async def get_repository_wrapper(session: AsyncSession = Depends(get_session)) -> RepositoryWrapper:
    """
    Returns the repository wrapper (Unit of Work).
    """

    return RepositoryWrapper(session)


def get_semantic_search_service(uow: RepositoryWrapper = Depends(get_repository_wrapper)) -> ISemanticSearchService:
    """
    Returns the semantic search service.
    """

    return SemanticSearchService(
        embedding_provider=get_embedding_provider(),
        vector_store_repository=get_vector_store_repository(),
        repository_wrapper=uow
    )


def get_discovery_agent_service(uow: RepositoryWrapper = Depends(get_repository_wrapper)) -> IDiscoveryAgentService:
    """
    Returns the discovery agent service with a single LLM model for both intent and synthesis.
    """

    return DiscoveryAgentService(
        semantic_search_service=get_semantic_search_service(uow),
        llm_provider=get_llm_provider()
    )


def get_zip_downloader() -> ZipDownloader:
    """
    Returns the zip downloader.
    """

    return ZipDownloader()


def get_rocrate_parser() -> ROCrateParser:
    """
    Returns the RO-Crate parser.
    """

    return ROCrateParser()


def get_pdf_extractor() -> PdfDocumentExtractor:
    """
    Returns the PDF extractor.
    """

    return PdfDocumentExtractor()


def get_word_extractor() -> WordDocumentExtractor:
    """
    Returns the Word document extractor.
    """

    return WordDocumentExtractor()


def get_rtf_extractor() -> RtfDocumentExtractor:
    """
    Returns the RTF extractor.
    """

    return RtfDocumentExtractor()


async def get_embedding_service(uow: RepositoryWrapper = Depends(get_repository_wrapper)) -> IEmbeddingService:
    """
    Returns the embedding ingestion service.
    """

    return EmbeddingService(
        repository_wrapper=uow,
        semantic_search_service=get_semantic_search_service(uow),
        zip_downloader=get_zip_downloader(),
        ro_crate_parser=get_rocrate_parser(),
        pdf_extractor=get_pdf_extractor(),
        word_extractor=get_word_extractor(),
        rtf_extractor=get_rtf_extractor()
    )
