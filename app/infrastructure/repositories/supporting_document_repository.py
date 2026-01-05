from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.repositories.i_supporting_document_repository import ISupportingDocumentRepository
from app.domain.entities.supporting_document import SupportingDocument
from app.domain.value_objects.metadata_constants import SupportingDocumentConstants
from app.infrastructure.data_access.base_repository import BaseRepository


class SupportingDocumentRepository(BaseRepository[SupportingDocument], ISupportingDocumentRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(SupportingDocument, session)

    async def find_supporting_zips_by_dataset_id(self, dataset_metadata_id: int) -> List[SupportingDocument]:

        result = await self.session.execute(
            select(self.model).filter(
                self.model.dataset_metadata_id == dataset_metadata_id,
                self.model.title == SupportingDocumentConstants.SUPPORTING_INFORMATION_TITLE,
                self.model.type == SupportingDocumentConstants.INFORMATION_TYPE,
                self.model.download_url.like(SupportingDocumentConstants.ZIP_EXTENSION_PATTERN)
            )
        )

        return list(result.scalars().all())

