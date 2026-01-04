[[_TOC_]]

# **Overview**

The **AI Search & Intelligence Engine** is the "Heavy Lifting" component of the system. It receives instructions from the Ingestion Hub, downloads actual scientific files, extracts their text, and builds a sophisticated semantic search index.

# **Requirements**
- **Runtime**: Python 3.10+
- **Environment**: Virtual Environment (`venv`)
- **Vector Store**: Qdrant or ChromaDB
- **NLP Model**: `all-MiniLM-L6-v2` (Sentence-Transformers)

# **Setup**

## **Dependencies**

All requirements are managed via `requirements.txt`.

1. Activate the environment: `.\venv\Scripts\activate`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Ensure the vector store service (e.g., Qdrant) is running.

# **User Guide**

## **The "Heavy Lifting" Workflow**

When triggered, the engine performs the following automated steps:

|Step|Action|Description|
|--|--|--|
|**1. Resource Retrieval**|Remote Download|Retrieves ZIP packages using the metadata URLs provided by the Hub.|
|**2. Package Extraction**|RO-Crate Parsing|Opens ZIP files and reads metadata to locate `.pdf` and `.docx` files.|
|**3. Text Extraction**|Deep Reading|Converts scientific text from documents into AI-readable formats.|
|**4. Vector Indexing**|Semantic Storage|Breaks text into concepts and saves them in the **Semantic Vault**.|

## **Search Capabilities**

|Capability|Description|
|--|--|
|**Natural Language**|Ask questions like: *"What datasets discuss carbon levels in soils?"*|
|**Concept Linking**|Finds results by understanding synonyms, even if exact words are missing.|
|**Deep Search**|Retrieves results based on content found **inside** attached PDF reports.|

# **Operating Instructions**

## **Performing a Search**
Use the `/search/semantic` endpoint to enter your query. 
- **Filtering**: Restrict searches to specific `content_types` (e.g., Titles only).
- **Thresholds**: Adjust `min_score` to filter out low-confidence matches.

## **Managing AI Memory**
If a dataset is removed or needs updating:
1. Use **Delete Embeddings** to wipe the AI's memory of a specific dataset.
2. Trigger a **Reprocess** from the Ingestion Hub to rebuild the index.

# **Troubleshooting**

|Issue|Potential Cause|Resolution|
|--|--|--|
|**Slow First Run**|AI Model is downloading.|Wait for the ~500MB model download to complete on first launch.|
|**Search Returns 0 Results**|Indexing in progress.|Wait 30 seconds after ingestion for the "Heavy Lifting" to finish.|
|**Vector Store Error**|Database disconnected.|Check that Qdrant/Chroma is running on the expected port.|

# **Verification & Testing**

To verify processing success:
1. Navigate to: `http://localhost:8000/docs`
2. Use the `/search/semantic` endpoint.
3. Type a specific sentence from an uploaded PDF.
4. A high similarity score (0.9+) confirms successful ingestion.

