from unittest.mock import AsyncMock, Mock

from datetime import datetime

import pytest

from app.domain.entities.supporting_document import SupportingDocument
from app.domain.value_objects.metadata_constants import SupportingDocumentConstants
from app.infrastructure.repositories.supporting_document_repository import SupportingDocumentRepository


class TestSupportingDocumentRepository:

    def setup_method(self):
        self.mock_session = Mock()
        self.repo = SupportingDocumentRepository(self.mock_session)
        self.supporting_info = SupportingDocument()
        self.supporting_info.supporting_document_id = 1
        self.supporting_info.title = SupportingDocumentConstants.SUPPORTING_INFORMATION_TITLE
        self.supporting_info.type = SupportingDocumentConstants.INFORMATION_TYPE
        self.supporting_info.download_url = "http://files/info.zip"
        self.supporting_info.document_type = "ZIP"
        self.supporting_info.created_at = datetime.utcnow()

        self.other_doc = SupportingDocument()
        self.other_doc.supporting_document_id = 2
        self.other_doc.title = "Other"
        self.other_doc.download_url = "http://files/doc.pdf"

    @pytest.mark.asyncio
    async def test_find_supporting_zips_by_dataset_id_filters(self):

        matching_doc = self.supporting_info
        non_matching = self.other_doc

        scalar_result = Mock()
        scalar_result.all.return_value = [matching_doc]

        execute_result = Mock()
        execute_result.scalars.return_value = scalar_result

        self.mock_session.execute = AsyncMock(return_value=execute_result)

        found = await self.repo.find_supporting_zips_by_dataset_id(42)

        self.mock_session.execute.assert_awaited_once()
        assert found == [matching_doc]

