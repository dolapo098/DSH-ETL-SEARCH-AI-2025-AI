from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.infrastructure.data_access.session import Base


class DatasetMetadata(Base):
    __tablename__ = "DatasetMetadatas"

    dataset_metadata_id = Column("DatasetMetadataID", Integer, primary_key=True, autoincrement=True)
    dataset_id = Column("DatasetID", String, nullable=False)
    file_identifier = Column("FileIdentifier", String, nullable=False)
    title = Column("Title", String, nullable=True)
    description = Column("Description", Text, nullable=True)
    publication_date = Column("PublicationDate", DateTime, nullable=False)
    metadata_date = Column("MetaDataDate", DateTime, nullable=False)
    created_at = Column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column("UpdatedAt", DateTime, nullable=True)

