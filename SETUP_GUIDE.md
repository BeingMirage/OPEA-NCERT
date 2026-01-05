# OPEA RAG Pipeline - Setup & Usage Guide

## Overview

This guide walks you through setting up and using the OPEA-based NCERT Doubt-Solver system.

**What you have:**
- ✅ 72 chunks.jsonl files with NCERT content (metadata-rich)
- ✅ OPEA architecture with microservices
- ✅ Vector database (Chroma) for fast retrieval
- ✅ Multilingual embedding model (supports 100+ languages)
- ✅ Language detection and smart routing
- ✅ RAG pipeline for question answering

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENT QUESTION                         │
│              "What is photosynthesis?"                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         LANGUAGE ROUTER (Detect language, grade)            │
│    → Language: English                                       │
│    → Grade: 7 (from query or user profile)                   │
│    → Subject: Science (inferred)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         EMBEDDING SERVICE (Query → Vector)                   │
│    → Convert question to 384-dim vector                      │
│    → Using multilingual-e5-small model                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         CHROMA RETRIEVER (Vector Search)                     │
│    → Search vector DB with filters:                          │
│       • grade = "7"                                          │
│       • subject = "Science"                                  │
│    → Find 5 most similar chunks                              │
│    → Return with scores                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         LLM SERVICE (Generate Answer) [FUTURE]              │
│    → Use top-3 chunks as context                             │
│    → Generate student-friendly answer                        │
│    → Add citations                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 FORMATTED RESPONSE                           │
│    ✓ Answer with sources                                     │
│    ✓ Citations with chunk IDs                                │
│    ✓ Grade-appropriate language                              │
│    ✓ Confidence score                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: System Requirements

### Storage & Runtime for Chroma
- No Docker required (runs inside the Python process)
- Ensure at least 2GB free disk space for `chroma_db/`
- Use a fast SSD for best retrieval speed

### Python 3.10+
Verify: `python --version`

---

## Step 2: Install Python Dependencies

```bash
# Navigate to project directory
cd c:\Users\ameyg\Desktop\PythonProjects\OPEA-RAG

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# This will download:
# - chromadb (vector store client)
# - sentence-transformers (embedding model)
# - langchain (pipeline framework)
# - transformers (LLM support)
# - langdetect (language detection)
# - fastapi/uvicorn (API endpoints - future)
```

**First run note:** 
- First `sentence-transformers` import will download the model (~1.3GB)
- Only happens once, then cached locally
- Required: Good internet connection initially

---

docker-compose up -d
docker-compose ps
## Step 3: Initialize the Chroma Vector Store

Chroma stores vectors on disk inside the project (default: `./chroma_db`).

- No containers or external services are required.
- The directory is created automatically the first time `setup.py` runs.
- To reset the store, delete the folder or call `setup_chroma(recreate=True)`.
- To move it, pass `persist_directory="D:/fast-ssd/chroma"` to `setup_chroma`.

You can quickly verify things by running `python setup.py`. The script logs when the
client connects and when the collection becomes available.

---

## Step 4: Initialize the System

### Quick Start
```bash
# Run setup script
python setup.py

# This will:
# 1. Initialize Chroma (creates ./chroma_db)
# 2. Load embedding model (~1.3GB download first time)
# 3. Create vector collection (table)
# 4. Test connection
```

### Index Chunks (One-time setup)
Edit `setup.py` and uncomment the indexing section:

```python
# Around line 48 in setup.py
index_result = index_all_chunks(
    vector_db, 
    embedding_service,
    root_dir="output",
    grade_filter=["5", "6", "7", "8"],  # All grades
    subject_filter=None  # All subjects
)
```

**Indexing time:** ~5-10 minutes for 72 files (first time only)

```bash
python setup.py
# [Progress bars will show...]
# ✓ Indexed 50000+ chunks
```

---

## Step 5: Test the System

Run the test suite to verify everything works:

```bash
python test_pipeline.py
```

This will:
1. ✓ Test language detection (English, Hindi, Bengali)
2. ✓ Test query analysis and routing
3. ✓ Test embedding service
4. ✓ Test Chroma connection and retrieval
5. ✓ Run complete RAG pipeline

**Expected output:**
```
[INFO] Language Detection Test
  → English (en) - 95.23%
  → Hindi (hi) - 94.12%

[INFO] Query Routing Test
  Query: "Class 7 science: What is photosynthesis?"
  → Detected Grade: 7
  → Detected Subject: Science
  → Strategy: grade_subject_filtered

[INFO] Retrieval Test
  Found 5 results for "photosynthesis"
  1. [Science_7_English] Process where plants...
  2. [Science_7_Hindi] पौधों में प्रकाश...
  ...
```

---

## Step 6: Use the Pipeline

### Simple Query Example

```python
from setup import main
from src.pipeline.rag_pipeline import create_rag_pipeline

# Initialize (or use from setup.py)
pipeline = main()

# Ask a question
response = pipeline.process_query(
    query="What is photosynthesis?",
    user_grade="7"
)

# Access response
print(response['answer'])
print(f"Sources: {response['num_sources']}")
for citation in response['citations']:
    print(f"  - {citation['source']}: {citation['excerpt']}")
```

### Response Structure

```python
{
    'query': 'What is photosynthesis?',
    'answer': 'Based on NCERT curriculum...',
    'language': {
        'lang_code': 'en',
        'lang_name': 'English',
        'confidence': 0.95
    },
    'grade': '7',
    'subject': 'Science',
    'retrieval_strategy': 'grade_subject_filtered',
    'citations': [
        {
            'source': 'Science_7_English',
            'grade': '7',
            'subject': 'Science',
            'excerpt': 'Photosynthesis is the process...'
        },
        ...
    ],
    'num_sources': 5,
    'timestamp': '2024-01-05T...',
    'status': 'success'
}
```

---

## Common Issues & Solutions

### Issue 1: "Cannot initialize Chroma"
```
Error: chromadb.errors.InvalidDimensionException ...
```
**Solution:**
- Delete the `chroma_db/` folder and rerun `python setup.py`
- Ensure the process has write access to the repository folder
- Override the storage path: `setup_chroma(persist_directory="D:/fast/chroma")`

### Issue 2: "Model downloading... very slow"
First import of sentence-transformers downloads ~1.3GB model.
- It's a one-time operation
- Check internet connection
- Estimated time: 2-5 minutes

### Issue 3: "Vector store empty"
- Run `python setup.py` with the indexing block enabled
- Confirm `index_all_chunks` printed a success message
- Inspect `chroma_db/` size (>50MB indicates data exists)

### Issue 4: "CUDA out of memory"
If using GPU and getting memory errors:
```python
# In embedding_service.py, set device to CPU:
self.model = SentenceTransformer(self.model_name, device='cpu')
```

---

## File Structure Reference

```
OPEA-RAG/
├── src/
│   ├── services/
│   │   ├── embedding_service.py      # Convert text → vectors
│   │   └── language_router.py        # Detect language & route
│   ├── vectordb/
│   │   ├── milvus_config.py         # Vector DB setup
│   │   └── indexer.py               # Index chunks
│   └── pipeline/
│       └── rag_pipeline.py          # Main RAG orchestrator
│
├── docker/
│   └── docker-compose.yml           # Legacy Milvus setup (optional)
│
├── output/                          # Indexed NCERT content
│   ├── 5/, 6/, 7/, 8/              # Grade folders
│   └── [subject]/[filename]/
│       ├── chunks.jsonl             # Your extracted data
│       ├── document.md
│       └── document.txt
│
├── setup.py                        # Initialize everything
├── test_pipeline.py                # Run tests
├── requirements.txt                # Python packages
└── README.md                       # Documentation
```

---

## Next Steps After Setup

1. **Fine-tune embedding model** (optional)
   - Use student feedback to improve relevance
   - See `Finetuning.md` for guide

2. **Add LLM service**
   - Currently returns chunk-based answers
   - Plan: Integrate Ollama or HuggingFace models
   - See `LLM_Integration.md`

3. **Build web interface**
   - Create FastAPI backend (use services in containers)
   - Build React/Vue frontend
   - Mobile support with React Native

4. **Evaluation & metrics**
   - Create benchmark dataset
   - Measure retrieval quality (precision@5)
   - Measure answer quality (BLEU, ROUGE scores)

---

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Language detection | ~50ms | Per query |
| Query embedding | ~100ms | Using multilingual-e5-small |
| Vector search | ~50ms | For 1 grade/subject filtered |
| Full pipeline | ~200-300ms | No LLM included |
| Indexing 1000 chunks | ~30s | First time only |
| Chroma init | Instant | Embedded client |

---

## Architecture Decision Rationale

### Why Chroma?
- Open-source, no vendor lock-in
- HNSW indexing (fast similarity search)
- Supports filtering (grade, subject, language)
- Scales to millions of vectors
- Works offline without Docker (friendly for Windows users)

### Why sentence-transformers?
- Multilingual (100+ languages)
- Lightweight (384 dimensions)
- Fast inference (multilingual-e5-small: 100ms/query)
- Pre-trained on 200M+ text pairs
- Easy to fine-tune

### Why LangChain?
- OPEA aligns with LangChain patterns
- Easy to compose chains (retriever → LLM → formatter)
- Rich ecosystem of integrations
- Good for prototyping RAG systems

---

## Debugging Tips

**Enable verbose logging:**
```python
# In any script
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Monitor Chroma:**
```bash
# Count stored entities
python - <<'PY'
from chromadb import PersistentClient
client = PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("ncert_chunks")
print("Entities:", collection.count())
PY
```

**Profile embedding speed:**
```python
import time
from src.services.embedding_service import get_embedding_service

service = get_embedding_service()
text = "What is photosynthesis?"

start = time.time()
embedding = service.embed_text(text)
print(f"Time: {(time.time()-start)*1000:.1f}ms")
```

---

## Support & Questions

For detailed module documentation:
- [OPEA_EXPLANATION.md](OPEA_EXPLANATION.md) - Architecture concepts
- [src/vectordb/milvus_config.py](src/vectordb/milvus_config.py) - Vector DB docs
- [src/services/embedding_service.py](src/services/embedding_service.py) - Embedding docs
- [src/pipeline/rag_pipeline.py](src/pipeline/rag_pipeline.py) - Pipeline docs

---

**Happy doubts solving! 🎓**
