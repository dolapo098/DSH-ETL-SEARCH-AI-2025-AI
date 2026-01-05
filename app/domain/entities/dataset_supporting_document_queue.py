from sqlalchemy import Column, DateTime, ForeignKey, Integer, Boolean

from app.infrastructure.data_access.session import Base


class DatasetSupportingDocumentQueue(Base):
    __tablename__ = "DatasetSupportingDocumentQueues"

    dataset_supporting_document_queue_id = Column("DatasetSupportingDocumentQueueID", Integer, primary_key=True, autoincrement=True)
    dataset_metadata_id = Column("DatasetMetadataID", Integer, ForeignKey("DatasetMetadatas.DatasetMetadataID"), nullable=False)
    processed_title_for_embedding = Column("ProcessedTitleForEmbedding", Boolean, default=False, nullable=False)
    processed_abstract_for_embedding = Column("ProcessedAbstractForEmbedding", Boolean, default=False, nullable=False)
    processed_supporting_docs_for_embedding = Column("ProcessedSupportingDocsForEmbedding", Boolean, default=False, nullable=False)
    is_processing = Column("IsProcessing", Boolean, default=False, nullable=False)
    created_at = Column("CreatedAt", DateTime, nullable=False)
    updated_at = Column("UpdatedAt", DateTime, nullable=True)
    last_updated_at = Column("LastUpdatedAt", DateTime, nullable=True)

