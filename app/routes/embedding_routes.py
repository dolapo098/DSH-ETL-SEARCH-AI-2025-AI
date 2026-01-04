from fastapi import APIRouter, Depends

from app.controllers.embedding_controller import EmbeddingController
from app.contracts.dtos.embedding_dtos import IndexEmbeddingResponse, IngestMetadataRequest, ProcessDatasetRequest
from app.contracts.services.i_embedding_service import IEmbeddingService
from app.infrastructure.di import get_embedding_service

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])
controller = EmbeddingController()


@router.post("/ingest-metadata", response_model=IndexEmbeddingResponse)
async def ingest_metadata(
    request: IngestMetadataRequest,
    service: IEmbeddingService = Depends(get_embedding_service)
) -> IndexEmbeddingResponse:

    return await controller.ingest_metadata(request, service)


@router.post("/process-dataset", response_model=IndexEmbeddingResponse)
async def process_dataset(
    request: ProcessDatasetRequest,
    service: IEmbeddingService = Depends(get_embedding_service)
) -> IndexEmbeddingResponse:

    return await controller.process_dataset(request, service)

