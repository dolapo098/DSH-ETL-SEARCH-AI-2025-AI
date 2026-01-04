from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.middleware.api_exception_handlers import register_exception_handlers
from app.controllers.embedding_controller import router as embedding_router
from app.controllers.search_controller import router as search_router


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

