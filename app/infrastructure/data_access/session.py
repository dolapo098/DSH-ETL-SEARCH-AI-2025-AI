import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Point to shared database in workspace root
# From: app/infrastructure/data_access/ -> app/infrastructure/ -> app/ -> DSH-ETL-SEARCH-AI-2025-AI/ -> DSH-ETL-2025/
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_file_dir, "../../../"))
_workspace_root = os.path.dirname(_project_root)
DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(_workspace_root, "etl_database.db")
)
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"timeout": 10}
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

