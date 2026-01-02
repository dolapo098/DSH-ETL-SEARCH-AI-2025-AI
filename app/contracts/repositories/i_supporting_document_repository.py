from typing import List, Protocol

from app.contracts.repositories.i_base_repository import IBaseRepository
from app.domain.entities.supporting_document import SupportingDocument


class ISupportingDocumentRepository(IBaseRepository[SupportingDocument], Protocol):
    """
    Interface for the supporting document repository.
    """

    async def find_supporting_zips_by_dataset_id(self, dataset_metadata_id: int) -> List[SupportingDocument]:
        """
        Retrieves supporting ZIP documents for a specific dataset metadata identifier.

        Args:
            dataset_metadata_id (int): The identifier of the dataset metadata.

        Returns:
            List[SupportingDocument]: A list of supporting ZIP documents.
        """
        ...

