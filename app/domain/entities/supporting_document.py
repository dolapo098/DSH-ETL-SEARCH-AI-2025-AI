from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.infrastructure.data_access.session import Base


class SupportingDocument(Base):
    __tablename__ = "SupportingDocuments"

    supporting_document_id = Column("SupportingDocumentID", Integer, primary_key=True, autoincrement=True)
    dataset_metadata_id = Column("DatasetMetadataID", Integer, ForeignKey("DatasetMetadata.DatasetMetadataID"), nullable=False)
    file_identifier = Column("FileIdentifier", String, nullable=False)
    title = Column("Title", String, nullable=True)
    description = Column("Description", Text, nullable=True)
    type = Column("Type", String, nullable=True)
    document_type = Column("DocumentType", String, nullable=True)
    download_url = Column("DownloadUrl", String, nullable=True)
    created_at = Column("CreatedAt", DateTime, nullable=False)
    updated_at = Column("UpdatedAt", DateTime, nullable=True)

