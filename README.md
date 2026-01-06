[[_TOC_]]

# **Overview**

The **AI Search & Intelligence Engine** is the "Heavy Lifting" component of the system. It receives instructions from the Ingestion Hub, downloads actual scientific files, extracts their text, and builds a sophisticated semantic search index.

# **Requirements**

- **Runtime**: Python 3.10+
- **Environment**: Virtual Environment (`venv`)
- **Vector Store**: Qdrant (deployed via Docker)
- **Relational Store**: SQLite (shared with .NET service)
- **NLP Model**: `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Unit Test**: Pytest

# **Setup**

## **Infrastructure (Docker)**

The vector database is hosted in Qdrant. Ensure it is running via Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## **Dependencies**

All requirements are managed via `requirements.txt`.

1. Activate the environment: `.\venv\Scripts\activate`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Ensure the Qdrant service is running.

# **Database & Storage**

The database and logging system share the same space at the root of the solution, ensuring a centralized location for persistence and audit trails across both the .NET and Python services.

- **Relational Database (SQLite)**:

  - **File Name**: `etl_database.db`
  - **Physical Location**: Accessible within the same directory with the Project folder

- **System Logs**:

  - **Location**: Found in the `\logs` Accessible within the same directory with the Project folder
  - **Files**: `python-service.log` and `etl-*.log`.

- **Vector Storage (Qdrant)**:
  - **Technology**: Qdrant Vector Database (running in Docker).
  - **Collection**: `embeddings`.

# **User Guide**

## **The "Heavy Lifting" Workflow**

When triggered, the engine performs the following automated steps:

| Step                      | Action           | Description                                                                   |
| ------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| **1. Resource Retrieval** | Remote Download  | Retrieves ZIP packages using the metadata URLs provided by the Hub.           |
| **2. Package Extraction** | RO-Crate Parsing | Opens ZIP files and reads metadata to locate **.pdf, .docx, and .rtf** files. |
| **3. Text Extraction**    | Deep Reading     | Converts scientific text from documents into AI-readable formats.             |
| **4. Vector Indexing**    | Semantic Storage | Breaks text into concepts and saves them in the **Semantic Vault**.           |

## **Search Capabilities**

| Capability              | Description                                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Smart Deduplication** | Collapses results by dataset identifier, returning only the **highest-scoring chunk** per dataset to prevent response flooding. |
| **Natural Language**    | Ask questions like: _"What datasets discuss carbon levels in soils?"_                                                           |
| **Concept Linking**     | Finds results by understanding synonyms, even if exact words are missing.                                                       |
| **Deep Search**         | Retrieves results based on content found **inside** attached reports (PDF, Word, RTF).                                          |

# **Operating Instructions**

## **Performing a Search**

You can interact with the service directly via the **Swagger UI**:

- **API URL**: `http://localhost:8000/docs`
- **Endpoint**: `/search/semantic`
- **Filtering**: Restrict searches to specific `content_types` (e.g., Titles only).

## **Inspecting the Vector Store**

Monitor embeddings and collection status via the **Qdrant Dashboard**:

- **URL**: [http://localhost:6333/dashboard#/collections/embeddings](http://localhost:6333/dashboard#/collections/embeddings)

## **Managing AI Memory**

If a dataset is removed or needs updating:

1. Use **Delete Embeddings** to wipe the AI's memory of a specific dataset.
2. Trigger a **Reprocess** from the Ingestion Hub to rebuild the index.

# **Troubleshooting**

| Issue                        | Potential Cause          | Resolution                                                            |
| ---------------------------- | ------------------------ | --------------------------------------------------------------------- |
| **Slow First Run**           | AI Model is downloading. | Wait for the ~500MB model download to complete on first launch.       |
| **Search Returns 0 Results** | Indexing in progress.    | Wait 30 seconds after ingestion for the "Heavy Lifting" to finish.    |
| **Vector Store Error**       | Database disconnected.   | Check that Qdrant is running on port 6333. Run `docker ps` to verify. |

# **Verification & Testing**

To verify processing success:

1. Navigate to: `http://localhost:8000/docs`
2. Use the `/search/semantic` endpoint.
3. Type a specific sentence from an uploaded document.
4. A high similarity score (0.9+) confirms successful ingestion.
