from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.dataset_metadata import DatasetMetadata
from app.infrastructure.repositories.dataset_metadata_repository import DatasetMetadataRepository


class TestDatasetMetadataRepository:

    def setup_method(self):

        self.mock_session = Mock()
        self.repository = DatasetMetadataRepository(self.mock_session)
        self.expected_metadata = DatasetMetadata(
            dataset_id="DSH-001",
            file_identifier="file-123",
            title="Meta Title",
            description="Meta description",
            publication_date=datetime.utcnow(),
            metadata_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.expected_metadata.author = "Tester"

    @pytest.mark.asyncio
    async def test_get_by_id_calls_session(self):

        getter = AsyncMock(return_value=self.expected_metadata)
        self.mock_session.get = getter

        result = await self.repository.get_by_id(5)

        getter.assert_awaited_once_with(DatasetMetadata, 5)
        assert result is self.expected_metadata

