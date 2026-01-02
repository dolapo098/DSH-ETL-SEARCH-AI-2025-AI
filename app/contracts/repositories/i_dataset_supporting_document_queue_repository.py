from typing import List, Protocol

from app.contracts.repositories.i_base_repository import IBaseRepository
from app.domain.entities.dataset_supporting_document_queue import DatasetSupportingDocumentQueue


class IDatasetSupportingDocumentQueueRepository(IBaseRepository[DatasetSupportingDocumentQueue], Protocol):
    """
    Interface for the dataset supporting document queue repository.
    """

    async def get_pending_queue_items(self) -> List[DatasetSupportingDocumentQueue]:
        """
        Retrieves all pending items from the document queue.

        Returns:
            List[DatasetSupportingDocumentQueue]: A list of pending queue items.
        """
        ...

