from fastapi import Depends, APIRouter

from app.contracts.dtos.embedding_dtos import IndexEmbeddingResponse, IngestMetadataRequest, ProcessDatasetRequest
from app.contracts.services.i_embedding_service import IEmbeddingService
from app.infrastructure.config.di import get_embedding_service

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.post("/ingest-metadata", response_model=IndexEmbeddingResponse)
async def ingest_metadata(
    request: IngestMetadataRequest,
    service: IEmbeddingService = Depends(get_embedding_service)
) -> IndexEmbeddingResponse:

    return IndexEmbeddingResponse(success=True, message="Metadata ingested successfully")


@router.post("/process-dataset", response_model=IndexEmbeddingResponse)
async def process_dataset(
    request: ProcessDatasetRequest,
    service: IEmbeddingService = Depends(get_embedding_service)
) -> IndexEmbeddingResponse:

    success = await service.process_dataset_heavy_lifting(
        dataset_metadata_id=request.datasetMetadataID
    )

    return IndexEmbeddingResponse(
        success=success,
        message="Dataset processed successfully" if success else "Failed to process dataset"
    )

