from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.repositories.i_dataset_metadata_repository import IDatasetMetadataRepository
from app.domain.entities.dataset_metadata import DatasetMetadata
from app.infrastructure.data_access.base_repository import BaseRepository


class DatasetMetadataRepository(BaseRepository[DatasetMetadata], IDatasetMetadataRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(DatasetMetadata, session)

