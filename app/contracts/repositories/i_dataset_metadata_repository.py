from typing import Protocol

from app.contracts.repositories.i_base_repository import IBaseRepository
from app.domain.entities.dataset_metadata import DatasetMetadata


class IDatasetMetadataRepository(IBaseRepository[DatasetMetadata], Protocol):
    """
    Interface for the dataset metadata repository.
    """
    ...

