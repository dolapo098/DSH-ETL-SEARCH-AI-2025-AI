from functools import lru_cache
from fastapi import Depends
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.embedding_service import EmbeddingService
from app.application.services.semantic_search_service import SemanticSearchService
from app.contracts.providers.i_embedding_provider import IEmbeddingProvider
from app.contracts.services.i_embedding_service import IEmbeddingService
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper
from app.infrastructure.data_access.session import AsyncSessionLocal
from app.infrastructure.parsers.rocrate_parser import ROCrateParser
from app.infrastructure.providers.pdf_document_extractor import PdfDocumentExtractor
from app.infrastructure.providers.sentence_transformer_embedding_provider import SentenceTransformerEmbeddingProvider
from app.infrastructure.providers.word_document_extractor import WordDocumentExtractor
from app.infrastructure.providers.zip_downloader import ZipDownloader
from app.infrastructure.repositories.qdrant_vectore_store_repository import QdrantVectorStoreRepository


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embedding_provider() -> IEmbeddingProvider:
    
    return SentenceTransformerEmbeddingProvider(get_embedding_model())


def get_vector_store_repository() -> QdrantVectorStoreRepository:
    
    return QdrantVectorStoreRepository(
        url="http://localhost:6333",
        collection_name="embeddings",
        vector_size=384
    )


async def get_session():
    
    async with AsyncSessionLocal() as session:
        
        yield session


async def get_repository_wrapper(session: AsyncSession = Depends(get_session)) -> RepositoryWrapper:
    
    return RepositoryWrapper(session)


def get_semantic_search_service(uow: RepositoryWrapper = Depends(get_repository_wrapper)) -> ISemanticSearchService:
    
    return SemanticSearchService(
        embedding_provider=get_embedding_provider(),
        vector_store_repository=get_vector_store_repository(),
        repository_wrapper=uow
    )


def get_zip_downloader() -> ZipDownloader:
    
    return ZipDownloader()


def get_rocrate_parser() -> ROCrateParser:
    
    return ROCrateParser()


def get_pdf_extractor() -> PdfDocumentExtractor:
    
    return PdfDocumentExtractor()


def get_word_extractor() -> WordDocumentExtractor:
    
    return WordDocumentExtractor()


async def get_embedding_service(uow: RepositoryWrapper = Depends(get_repository_wrapper)) -> IEmbeddingService:
    
    return EmbeddingService(
        repository_wrapper=uow,
        semantic_search_service=get_semantic_search_service(uow),
        zip_downloader=get_zip_downloader(),
        ro_crate_parser=get_rocrate_parser(),
        pdf_extractor=get_pdf_extractor(),
        word_extractor=get_word_extractor()
    )

