import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI

from app.infrastructure.middleware.api_exception_handlers import register_exception_handlers
from app.routes.embedding_routes import router as embedding_router
from app.routes.search_routes import router as search_router


def setup_logging():
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_file_dir))
    workspace_root = os.path.dirname(project_root)
    log_dir = os.path.join(workspace_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "python-service.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )


setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield


app = FastAPI(
    title="DSH ETL RAG Discovery Service",
    description="Semantic search service for dataset metadata",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(embedding_router)
app.include_router(search_router)

register_exception_handlers(app)
