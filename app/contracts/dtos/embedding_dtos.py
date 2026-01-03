from pydantic import BaseModel, Field


class IndexEmbeddingResponse(BaseModel):
    success: bool
    message: str


class IngestMetadataRequest(BaseModel):
    identifier: str = Field(..., min_length=1)
    contentType: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    sourceFile: str = Field(None)


class ProcessDatasetRequest(BaseModel):
    datasetMetadataID: int

