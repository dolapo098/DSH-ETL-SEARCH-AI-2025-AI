import io
import json
import logging
import os
import zipfile
from datetime import datetime

from app.contracts.services.i_embedding_service import IEmbeddingService
from app.contracts.services.i_semantic_search_service import ISemanticSearchService
from app.domain.value_objects.metadata_constants import SupportingDocumentConstants
from app.infrastructure.data_access.repository_wrapper import RepositoryWrapper

logger = logging.getLogger(__name__)


class EmbeddingService(IEmbeddingService):
    def __init__(
        self, 
        repository_wrapper: RepositoryWrapper,
        semantic_search_service: ISemanticSearchService,
        zip_downloader,
        ro_crate_parser,
        pdf_extractor,
        word_extractor,
        rtf_extractor
    ):
        self._repo = repository_wrapper
        self._semantic = semantic_search_service
        self._zip_downloader = zip_downloader
        self._ro_crate_parser = ro_crate_parser
        self._extractors = {
            ".pdf": pdf_extractor,
            ".docx": word_extractor,
            ".rtf": rtf_extractor
        }

    async def process_dataset_heavy_lifting(self, dataset_metadata_id: int) -> bool:

        if not dataset_metadata_id:
            
            return False

        metadata = await self._repo.dataset_metadata.get_by_id(dataset_metadata_id)
        
        if not metadata:
            
            return False

        if metadata.title:
            await self._semantic.ingest_text(
                identifier=metadata.file_identifier,
                content_type="title",
                text=metadata.title
            )

        if metadata.description:
            await self._semantic.ingest_text(
                identifier=metadata.file_identifier,
                content_type="description",
                text=metadata.description
            )

        supporting_document_zips = await self._repo.supporting_documents.find_supporting_zips_by_dataset_id(
            dataset_metadata_id
        )

        logger.info(f"Processing {len(supporting_document_zips)} supporting document zip(s) for dataset {metadata.file_identifier}")

        for supporting_document in supporting_document_zips:
            
            if supporting_document.download_url:
                await self._process_zip_package(supporting_document.download_url, metadata.file_identifier)
            else:
                logger.warning(f"Supporting document {supporting_document.supporting_document_id} has no download URL")
        
        queue_item = await self._repo.dataset_supporting_document_queues.get_single(
            dataset_metadata_id=dataset_metadata_id
        )

        if queue_item:
            queue_item.processed_title_for_embedding = True
            queue_item.processed_abstract_for_embedding = True
            queue_item.processed_supporting_docs_for_embedding = True
            queue_item.last_updated_at = datetime.utcnow()
            
            await self._repo.dataset_supporting_document_queues.update(queue_item)

        await self._repo.save_changes()
        
        return True

    async def _process_zip_package(self, download_url: str, identifier: str):

        try:
            zip_bytes = self._zip_downloader.download(download_url)
            
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                ro_crate = self._load_ro_crate(z)
                
                supported_files = self._ro_crate_parser.extract_supported_files(ro_crate)
                logger.info(f"Processing {len(supported_files)} file(s) from zip for identifier: {identifier}")
                
                for file_path in supported_files:
                    await self._extract_and_ingest_file(z, file_path, identifier)
                    
        except Exception as ex:
            logger.error(f"Failed processing supporting document zip from {download_url}: {str(ex)}", exc_info=True)

    def _load_ro_crate(self, z: zipfile.ZipFile) -> dict:

        if SupportingDocumentConstants.RO_CRATE_METADATA_FILE not in z.namelist():
            return {}
            
        with z.open(SupportingDocumentConstants.RO_CRATE_METADATA_FILE) as f:
            return json.load(f)

    async def _extract_and_ingest_file(self, z: zipfile.ZipFile, file_path: str, identifier: str):

        extension = os.path.splitext(file_path)[1].lower()
        extractor = self._extractors.get(extension)
        
        if not extractor or file_path not in z.namelist():
            return
            
        file_content = z.read(file_path)
        text = extractor.extract_text(file_content)
        
        if text:
            await self._semantic.ingest_text(
                identifier=identifier,
                content_type="document",
                text=text,
                source_file=file_path
            )
            logger.info(f"Indexed document: {file_path} ({len(text)} chars)")

