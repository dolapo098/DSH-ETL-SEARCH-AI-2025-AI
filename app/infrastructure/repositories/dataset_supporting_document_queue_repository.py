from typing import List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.repositories.i_dataset_supporting_document_queue_repository import IDatasetSupportingDocumentQueueRepository
from app.domain.entities.dataset_supporting_document_queue import DatasetSupportingDocumentQueue
from app.infrastructure.data_access.base_repository import BaseRepository


class DatasetSupportingDocumentQueueRepository(BaseRepository[DatasetSupportingDocumentQueue], IDatasetSupportingDocumentQueueRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(DatasetSupportingDocumentQueue, session)

    async def get_pending_queue_items(self) -> List[DatasetSupportingDocumentQueue]:
        stmt = select(self.model).filter(
            or_(
                self.model.processed_title_for_embedding == False,
                self.model.processed_abstract_for_embedding == False,
                self.model.processed_supporting_docs_for_embedding == False,
                (self.model.updated_at != None) & 
                (or_(self.model.last_updated_at == None, self.model.updated_at > self.model.last_updated_at))
            )
        )
        
        result = await self.session.execute(stmt)
        
        return list(result.scalars().all())

