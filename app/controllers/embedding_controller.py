from app.contracts.dtos.embedding_dtos import IndexEmbeddingResponse, IngestMetadataRequest, ProcessDatasetRequest
from app.contracts.services.i_embedding_service import IEmbeddingService


class EmbeddingController:
    """
    Controller handling embedding-related operations.
    """

    async def ingest_metadata(
        self,
        request: IngestMetadataRequest,
        service: IEmbeddingService
    ) -> IndexEmbeddingResponse:

        return IndexEmbeddingResponse(success=True, message="Metadata ingested successfully")

    async def process_dataset(
        self,
        request: ProcessDatasetRequest,
        service: IEmbeddingService
    ) -> IndexEmbeddingResponse:

        success = await service.process_dataset_heavy_lifting(
            dataset_metadata_id=request.datasetMetadataID
        )

        return IndexEmbeddingResponse(
            success=success,
            message="Dataset processed successfully" if success else "Failed to process dataset"
        )
