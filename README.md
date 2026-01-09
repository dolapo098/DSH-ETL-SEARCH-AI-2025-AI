# AI Search & Intelligence Engine

## Overview

The **AI Search & Intelligence Engine** is the core component of the DSH ETL Search & Discovery Platform. It provides intelligent semantic search capabilities and conversational AI assistance for discovering scientific datasets. The system uses advanced natural language processing to understand user queries, extract intent, and retrieve relevant datasets from a vector database.

Key capabilities include:

- **Semantic Search**: Natural language queries that understand context and synonyms
- **Conversational Agent**: AI-powered chat interface for dataset discovery
- **Vector Indexing**: Automatic extraction and embedding of scientific documents
- **Smart Deduplication**: Returns highest-scoring results per dataset to prevent flooding

---

## Requirements

| Component               | Specification                              |
| ----------------------- | ------------------------------------------ |
| **Runtime**             | Python 3.10+                               |
| **Environment**         | Virtual Environment (`venv`)               |
| **Vector Store**        | Qdrant (deployed via Docker)               |
| **Relational Database** | SQLite (shared with .NET service)          |
| **NLP Model**           | `all-MiniLM-L6-v2` (Sentence-Transformers) |
| **LLM Provider**        | Google Gemini (Free Tier)                  |
| **API Framework**       | FastAPI                                    |
| **Testing**             | Pytest                                     |

---

## Setup

### 1. Infrastructure (Docker)

Start the Qdrant vector database:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Verify Qdrant is running:

- **Dashboard**: http://localhost:6333/dashboard
- **Collection**: `embeddings`

### 2. Python Environment

1. Create and activate virtual environment:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_api_key_here
   LLM_MODEL=gemini-flash-latest
   ```
   Get your free API key at: https://aistudio.google.com

### 3. Database & Storage

- **SQLite Database**: `etl_database.db` (shared with .NET service)
- **Logs**: `logs/python-service.log`
- **Vector Store**: Qdrant collection `embeddings` on port 6333

### 4. Start the Service

```bash
# Set Python path
$env:PYTHONPATH="."  # Windows PowerShell
export PYTHONPATH="."  # Linux/Mac

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**API Documentation**: http://localhost:8001/docs

---

## User Guide

The following table describes all available functionalities in the system:

| Functionality            | Endpoint                      | Method | Description                                                                                                                                                                                                      | Use Case                                                                                                                   |
| ------------------------ | ----------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Semantic Search**      | `/search/semantic`            | POST   | Performs natural language search across indexed datasets. Returns results ranked by semantic similarity with deduplication (highest-scoring chunk per dataset).                                                  | Find datasets using conversational queries like "water quality data" or "climate change measurements"                      |
| **Delete Embeddings**    | `/search/delete-embeddings`   | POST   | Removes all vector embeddings for a specific dataset identifier from the vector store. Useful for reprocessing or removing outdated data.                                                                        | Clean up AI memory when a dataset is removed or needs re-indexing                                                          |
| **Ingest Metadata**      | `/embeddings/ingest-metadata` | POST   | Extracts and indexes metadata (title, abstract) from dataset records. Creates vector embeddings for semantic search.                                                                                             | Initial indexing of dataset metadata without processing supporting documents                                               |
| **Process Dataset**      | `/embeddings/process-dataset` | POST   | Full dataset processing pipeline: downloads ZIP packages, extracts supporting documents (PDF, DOCX, RTF), extracts text, and creates embeddings for deep content search.                                         | Complete indexing including document content for comprehensive search capabilities                                         |
| **Conversational Agent** | `/agent/chat`                 | POST   | AI-powered conversational interface for dataset discovery. Uses RAG (Retrieval-Augmented Generation) to understand user intent, search the vector store, and generate natural language responses with citations. | Interactive chat interface where users can ask questions about datasets in natural language and receive contextual answers |

### Example Usage

#### Semantic Search

```json
POST /search/semantic
{
  "query": "carbon levels in soil",
  "limit": 5,
  "offset": 0
}
```

#### Conversational Agent

```json
POST /agent/chat
{
  "message": "What datasets discuss coastal erosion?",
  "history": []
}
```

---

## Architecture

The system follows **Clean Architecture** principles with clear separation of concerns:

- **Controllers**: Handle HTTP requests/responses
- **Services**: Business logic orchestration
- **Repositories**: Data access abstraction
- **Providers**: External service integrations (LLM, embeddings)
- **Factories**: Provider creation with registry pattern

### Key Design Patterns

- **Strategy Pattern**: `ILLMProvider` interface for interchangeable LLM implementations
- **Factory Pattern**: `LLMProviderFactory` with dictionary-based registry
- **Dependency Injection**: FastAPI's `Depends()` for service wiring
- **Repository Pattern**: Abstracted data access layer

---

## Troubleshooting

| Issue                        | Potential Cause       | Resolution                                                 |
| ---------------------------- | --------------------- | ---------------------------------------------------------- |
| **Slow First Run**           | AI model downloading  | Wait for ~500MB model download to complete on first launch |
| **Search Returns 0 Results** | Indexing in progress  | Wait 30 seconds after ingestion for processing to finish   |
| **Vector Store Error**       | Qdrant disconnected   | Verify Qdrant is running: `docker ps` or check port 6333   |
| **API Error 429**            | Gemini quota exceeded | Check API usage limits or wait for quota reset             |
| **Connection Refused**       | Service not running   | Ensure uvicorn is running on port 8001                     |

---

## Verification & Testing

1. Navigate to: http://localhost:8001/docs
2. Use the `/search/semantic` endpoint
3. Type a specific sentence from an uploaded document
4. A high similarity score (0.9+) confirms successful ingestion

---

## License

This project is part of the DSH ETL Search & Discovery Platform.
