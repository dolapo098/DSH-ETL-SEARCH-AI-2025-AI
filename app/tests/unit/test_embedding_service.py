import io
import zipfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.services.embedding_service import EmbeddingService
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.domain.entities.dataset_metadata import DatasetMetadata
from app.domain.entities.dataset_supporting_document_queue import (
    DatasetSupportingDocumentQueue,
)
from app.domain.entities.supporting_document import SupportingDocument
from app.domain.value_objects.metadata_constants import SupportingDocumentConstants
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper


class TestEmbeddingService:
    DATASET_ID = 10
    IDENTIFIER = "dataset-10"
    DOWNLOAD_URL = "https://example.com/supporting.zip"
    ZIP_ENTRY = "supporting-documents/report.rtf"

    def setup_method(self):
        metadata = Mock(spec=DatasetMetadata)
        metadata.dataset_metadata_id = self.DATASET_ID
        metadata.file_identifier = self.IDENTIFIER
        metadata.title = "Important Title"
        metadata.description = "Detailed description"

        queue_item = Mock(spec=DatasetSupportingDocumentQueue)
        queue_item.dataset_supporting_document_queue_id = 1
        queue_item.processed_title_for_embedding = False
        queue_item.processed_abstract_for_embedding = False
        queue_item.processed_supporting_docs_for_embedding = False

        supporting_doc = Mock(spec=SupportingDocument)
        supporting_doc.supporting_document_id = 99
        supporting_doc.download_url = self.DOWNLOAD_URL

        self.mock_repo = Mock(spec=RepositoryWrapper)
        self.mock_repo.dataset_metadata.get_by_id = AsyncMock(return_value=metadata)
        self.mock_repo.supporting_documents.find_supporting_zips_by_dataset_id = AsyncMock(
            return_value=[supporting_doc]
        )
        self.mock_repo.dataset_supporting_document_queues.get_single = AsyncMock(
            return_value=queue_item
        )
        self.mock_repo.dataset_supporting_document_queues.update = AsyncMock()
        self.mock_repo.save_changes = AsyncMock()

        self.mock_semantic = Mock(spec=ISemanticSearchService)
        self.mock_semantic.ingest_text = AsyncMock()

        self.mock_zip_downloader = Mock()
        self.mock_ro_crate_parser = Mock()
        self.mock_pdf_extractor = Mock()
        self.mock_word_extractor = Mock()
        self.mock_rtf_extractor = Mock()

        self.mock_pdf_extractor.extract_text.return_value = ""
        self.mock_word_extractor.extract_text.return_value = ""
        self.mock_rtf_extractor.extract_text.return_value = "extracted rtf text"

        self.service = EmbeddingService(
            repository_wrapper=self.mock_repo,
            semantic_search_service=self.mock_semantic,
            zip_downloader=self.mock_zip_downloader,
            ro_crate_parser=self.mock_ro_crate_parser,
            pdf_extractor=self.mock_pdf_extractor,
            word_extractor=self.mock_word_extractor,
            rtf_extractor=self.mock_rtf_extractor,
        )

        self.mock_zip_downloader.download.return_value = self._build_supporting_zip()
        self.mock_ro_crate_parser.extract_supported_files.return_value = [
            self.ZIP_ENTRY
        ]

    def _build_supporting_zip(self) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr(SupportingDocumentConstants.RO_CRATE_METADATA_FILE, "{}")
            z.writestr(self.ZIP_ENTRY, "fake rtf content")
        buffer.seek(0)
        return buffer.getvalue()

    @pytest.mark.asyncio
    async def test_process_dataset_heavy_lifting_ingests_metadata_and_documents(self):
        result = await self.service.process_dataset_heavy_lifting(self.DATASET_ID)

        assert result is True
        self.mock_semantic.ingest_text.assert_any_await(
            identifier=self.IDENTIFIER,
            content_type="title",
            text="Important Title",
        )
        self.mock_semantic.ingest_text.assert_any_await(
            identifier=self.IDENTIFIER,
            content_type="description",
            text="Detailed description",
        )
        self.mock_semantic.ingest_text.assert_any_await(
            identifier=self.IDENTIFIER,
            content_type="document",
            text="extracted rtf text",
            source_file=self.ZIP_ENTRY,
        )
        self.mock_zip_downloader.download.assert_called_once_with(self.DOWNLOAD_URL)
        self.mock_ro_crate_parser.extract_supported_files.assert_called_once()
        self.mock_repo.dataset_supporting_document_queues.update.assert_awaited_once()
        assert self.mock_repo.dataset_supporting_document_queues.get_single.await_count == 1

    @pytest.mark.asyncio
    async def test_process_dataset_heavy_lifting_returns_false_when_metadata_missing(self):
        self.mock_repo.dataset_metadata.get_by_id = AsyncMock(return_value=None)

        result = await self.service.process_dataset_heavy_lifting(self.DATASET_ID)

        assert result is False
        self.mock_semantic.ingest_text.assert_not_called()
        self.mock_repo.dataset_supporting_document_queues.update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_extract_and_ingest_file_skips_unknown_extension(self):

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("ignored.txt", "ignored")
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as zf:
            await self.service._extract_and_ingest_file(zf, "ignored.txt", self.IDENTIFIER)

        self.mock_semantic.ingest_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_dataset_heavy_lifting_skips_documents_without_download_url(self):

        supporting_doc = Mock(spec=SupportingDocument)
        supporting_doc.download_url = None
        self.mock_repo.supporting_documents.find_supporting_zips_by_dataset_id = AsyncMock(
            return_value=[supporting_doc]
        )
        self.service._process_zip_package = AsyncMock()

        result = await self.service.process_dataset_heavy_lifting(self.DATASET_ID)

        assert result is True
        self.service._process_zip_package.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_process_zip_package_handles_download_errors(self):
        self.mock_zip_downloader.download.side_effect = Exception("download failure")

        await self.service._process_zip_package(self.DOWNLOAD_URL, self.IDENTIFIER)

        self.mock_semantic.ingest_text.assert_not_called()

