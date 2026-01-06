from unittest.mock import AsyncMock, Mock

from datetime import datetime, timedelta

import pytest

from app.domain.entities.dataset_supporting_document_queue import DatasetSupportingDocumentQueue
from app.infrastructure.repositories.dataset_supporting_document_queue_repository import (
    DatasetSupportingDocumentQueueRepository,
)


class TestDatasetSupportingDocumentQueueRepository:

    def setup_method(self):
        self.mock_session = Mock()
        self.repo = DatasetSupportingDocumentQueueRepository(self.mock_session)
        self.pending = DatasetSupportingDocumentQueue()
        self.pending.processed_title_for_embedding = False
        self.pending.processed_abstract_for_embedding = True
        self.pending.processed_supporting_docs_for_embedding = True
        self.pending.created_at = datetime.utcnow()
        self.pending.dataset_metadata_id = 10

        self.stale = DatasetSupportingDocumentQueue()
        self.stale.processed_title_for_embedding = True
        self.stale.processed_abstract_for_embedding = True
        self.stale.processed_supporting_docs_for_embedding = True
        self.stale.updated_at = datetime.utcnow()
        self.stale.last_updated_at = None
        self.stale.dataset_metadata_id = 10

    @pytest.mark.asyncio
    async def test_get_pending_queue_items_applies_filter(self):

        pending = DatasetSupportingDocumentQueue()
        stale = DatasetSupportingDocumentQueue()

        scalar_result = Mock()
        scalar_result.all.return_value = [pending, stale]

        execute_result = Mock()
        execute_result.scalars.return_value = scalar_result

        self.mock_session.execute = AsyncMock(return_value=execute_result)

        results = await self.repo.get_pending_queue_items()

        self.mock_session.execute.assert_awaited_once()
        assert pending in results
        assert stale in results

