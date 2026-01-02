from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.data_access.session import AsyncSessionLocal
from app.infrastructure.repositories.dataset_metadata_repository import DatasetMetadataRepository
from app.infrastructure.repositories.dataset_supporting_document_queue_repository import DatasetSupportingDocumentQueueRepository
from app.infrastructure.repositories.supporting_document_repository import SupportingDocumentRepository


class RepositoryWrapper:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._dataset_metadata = DatasetMetadataRepository(self.session)
        self._supporting_documents = SupportingDocumentRepository(self.session)
        self._dataset_supporting_document_queues = DatasetSupportingDocumentQueueRepository(self.session)

    @property
    def dataset_metadata(self):
        return self._dataset_metadata

    @property
    def supporting_documents(self):
        return self._supporting_documents

    @property
    def dataset_supporting_document_queues(self):
        return self._dataset_supporting_document_queues

    async def save_changes(self) -> None:
        try:
            await self.session.commit()
            
        except Exception:
            await self.session.rollback()
            
            raise

    async def execute_in_transaction(self, operation: Callable) -> Any:
        try:
            result = await operation()
            await self.session.commit()
            
            return result
            
        except Exception:
            await self.session.rollback()
            
            raise

    async def close(self):
        await self.session.close()

    async def __aenter__(self):

        if not self.session:
            self.session = AsyncSessionLocal()
            self._dataset_metadata.session = self.session
            self._supporting_documents.session = self.session
            self._dataset_supporting_document_queues.session = self.session
            
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if exc_type is not None:
            await self.session.rollback()
            
        else:
            await self.session.commit()
            
        await self.session.close()

