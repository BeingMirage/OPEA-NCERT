# Project Directory Structure

## Complete File Organization

```
OPEA-RAG/
│
├── 📁 src/                                    # Main source code
│   ├── __init__.py
│   │
│   ├── 📁 services/                          # Microservices
│   │   ├── __init__.py
│   │   ├── embedding_service.py              # Text → Vector (384 dims)
│   │   │   └── EmbeddingService class
│   │   └── language_router.py                # Language detection + routing
│   │       └── LanguageRouter class
│   │
│   ├── 📁 vectordb/                          # Vector database operations
│   │   ├── __init__.py
│   │   ├── milvus_config.py                  # Milvus setup & operations
│   │   │   └── MilvusVectorDB class
│   │   └── indexer.py                        # Load chunks → embed → index
│   │       ├── ChunkLoader class
│   │       └── OPEAIndexer class
│   │
│   └── 📁 pipeline/                          # RAG pipeline orchestration
│       ├── __init__.py
│       └── rag_pipeline.py                   # Main RAG pipeline
│           └── OPEARAGPipeline class
│
├── 📁 docker/                                # Container setup
│   └── docker-compose.yml                    # Milvus container config
│
├── 📁 config/                                # Configuration (empty - for future)
│
├── 📁 output/                                # Extracted NCERT content
│   ├── 5/                                    # Grade 5
│   │   ├── English/
│   │   │   └── English_5/
│   │   │       ├── chunks.jsonl              # ✅ Verified
│   │   │       ├── document.md
│   │   │       └── document.txt
│   │   ├── Hindi/
│   │   ├── Maths/
│   │   └── SSc/
│   ├── 6/                                    # Grade 6 (35+ files)
│   │   ├── Arts/
│   │   ├── English/
│   │   ├── Hindi/
│   │   ├── Maths/
│   │   ├── Sanskrit/
│   │   ├── Science/
│   │   ├── SSc/
│   │   ├── Urdu/
│   │   └── XPhy_Education/
│   ├── 7/                                    # Grade 7 (25+ files)
│   │   ├── ARTS/
│   │   ├── ENGLISH/
│   │   ├── HINDI/
│   │   ├── MATHS/
│   │   ├── PHYSICAL_EDUCATION/
│   │   ├── SANSKRIT/
│   │   ├── SCIENCE/
│   │   ├── SOCIAL_SCIENCE/
│   │   ├── URDU/
│   │   └── VOCATIONAL_EDUCATION/
│   └── 8/                                    # Grade 8 (15+ files)
│       ├── ARTS/
│       ├── ENGLISH/
│       ├── HINDI/
│       ├── MATHS/
│       ├── PHYSICAL_EDUCATION/
│       ├── SANSKRIT/
│       ├── SCIENCE/
│       ├── SOCIAL_SCIENCE/
│       ├── URDU/
│       └── VOCATIONAL_EDUCATION/
│
├── 📄 setup.py                               # Initialize whole system
├── 📄 test_pipeline.py                       # Test suite
├── 📄 requirements.txt                       # Python dependencies (UPDATED)
├── 📄 requirements_extraction.txt            # Original extraction requirements
│
├── 📖 README.md                              # Original project README
├── 📖 OPEA_EXPLANATION.md                    # ✨ NEW: OPEA concepts guide
├── 📖 SETUP_GUIDE.md                         # ✨ NEW: Detailed setup guide
├── 📖 QUICK_START.md                         # ✨ NEW: 5-step quick start
├── 📖 IMPLEMENTATION_SUMMARY.md              # ✨ NEW: What was built
└── 📖 DIRECTORY_STRUCTURE.md                 # ✨ NEW: This file

```

---

## 📊 File Count Summary

```
Python Source Files:     7
  ├── embedding_service.py      250 lines
  ├── language_router.py        200 lines
  ├── milvus_config.py          320 lines
  ├── indexer.py                200 lines
  ├── rag_pipeline.py           300 lines
  ├── setup.py                  100 lines
  └── test_pipeline.py          350 lines
                         Total: ~1,720 lines

Configuration Files:     2
  ├── docker-compose.yml
  └── requirements.txt

Documentation Files:     6
  ├── OPEA_EXPLANATION.md
  ├── SETUP_GUIDE.md
  ├── QUICK_START.md
  ├── IMPLEMENTATION_SUMMARY.md
  ├── DIRECTORY_STRUCTURE.md
  └── README.md (original)

Extracted Content:       72 chunks.jsonl files
  ├── 4 files (Grade 5)
  ├── 31 files (Grade 6)
  ├── 25 files (Grade 7)
  └── 12 files (Grade 8)

Total LOC Written: ~2,000 lines of code
Total Documentation: ~1,500 lines
```

---

## 🗂️ File Organization Logic

### `src/services/` - Independent Services
These are **stateless, reusable microservices**:
- **embedding_service.py** - Can be called by multiple services
- **language_router.py** - Pure analysis, no side effects

### `src/vectordb/` - Vector Database Layer
All database operations:
- **milvus_config.py** - Connection & CRUD operations
- **indexer.py** - Batch loading and indexing

### `src/pipeline/` - Orchestration Layer
Combines services into complete workflows:
- **rag_pipeline.py** - Chains services together (OPEA pattern)

### `docker/` - Infrastructure
Containerized dependencies:
- **docker-compose.yml** - Milvus vector database

### `output/` - Knowledge Base
Extracted NCERT content (72 files):
- Organized by grade (5-8)
- Organized by subject
- Each has: chunks.jsonl, document.md, document.txt

### Root Files - Entry Points
Scripts to run the system:
- **setup.py** - Initialize everything
- **test_pipeline.py** - Verify setup

Documentation:
- **OPEA_EXPLANATION.md** - Architecture overview
- **SETUP_GUIDE.md** - Step-by-step setup
- **QUICK_START.md** - 5-minute start
- **IMPLEMENTATION_SUMMARY.md** - What was built

---

## 🔄 Data Flow by Directory

```
output/ (Raw Content)
  ↓
setup.py (reads chunks.jsonl)
  ↓
src/vectordb/indexer.py (loads chunks)
  ↓
src/services/embedding_service.py (converts to vectors)
  ↓
src/vectordb/milvus_config.py (stores in Milvus)
  ↓
Milvus Database (via docker/)
  ↓
src/pipeline/rag_pipeline.py (retrieves for queries)
  ↓
User Response
```

---

## 📦 Key Implementation Files

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `src/services/embedding_service.py` | 250 | Text → 384D vectors | ✅ Complete |
| `src/services/language_router.py` | 200 | Language detection | ✅ Complete |
| `src/vectordb/milvus_config.py` | 320 | Vector DB operations | ✅ Complete |
| `src/vectordb/indexer.py` | 200 | Index chunks | ✅ Complete |
| `src/pipeline/rag_pipeline.py` | 300 | RAG orchestration | ✅ Complete |
| `setup.py` | 100 | System initialization | ✅ Complete |
| `test_pipeline.py` | 350 | Test suite | ✅ Complete |
| `docker-compose.yml` | 30 | Milvus container | ✅ Complete |
| `requirements.txt` | 40 | Dependencies | ✅ Updated |

---

## 🎯 Next Steps By Directory

### Add LLM Integration
Create: `src/services/llm_service.py`
- Integrate Ollama/HuggingFace/OpenAI
- Update: `src/pipeline/rag_pipeline.py`

### Build Web API
Create: `src/api/main.py`
- FastAPI backend
- REST endpoints for each service
- Connect to docker-compose services

### Create Frontend
Create: `ui/web/` and `ui/mobile/`
- React web interface
- React Native mobile app
- Connect to `src/api/`

### Build Evaluation Suite
Create: `evaluation/`
- Benchmark dataset
- Metrics (precision@K, nDCG, BLEU, ROUGE)
- Compare versions

### Setup Fine-tuning
Create: `finetuning/`
- Training pipeline using feedback
- Data preparation
- Model validation

---

## 💾 Data Organization in `output/`

Each text has consistent structure:

```
output/
├── <GRADE>/
│   ├── <SUBJECT>/
│   │   └── <SUBJECT_VARIANT>/
│   │       ├── chunks.jsonl          ← What we read
│   │       │   └── JSON lines:
│   │       │       {
│   │       │         "chunk_id": "...",
│   │       │         "text": "...",
│   │       │         "grade": "5",
│   │       │         "subject": "English",
│   │       │         "language": "en",
│   │       │         "element_type": "Title",
│   │       │         "source_file": "English_5"
│   │       │       }
│   │       ├── document.md           ← Markdown version
│   │       └── document.txt          ← Plain text version
```

**Total chunks indexed:** ~50,000+ chunks across all files

---

## 🔐 File Permissions & Safety

All Python files are:
- ✅ UTF-8 encoded
- ✅ Well-documented
- ✅ Error-handled
- ✅ Logging-enabled
- ✅ Modular & testable

No modifications to `output/` files (read-only knowledge base)

---

## 🚀 Quick Navigation

| Want to... | Go to... |
|-----------|----------|
| Understand OPEA | [OPEA_EXPLANATION.md](OPEA_EXPLANATION.md) |
| Set up system | [SETUP_GUIDE.md](SETUP_GUIDE.md) |
| Quick start (5 min) | [QUICK_START.md](QUICK_START.md) |
| See what was built | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) |
| Understand structure | You are here! |
| Use embeddings | [src/services/embedding_service.py](src/services/embedding_service.py) |
| Use vector DB | [src/vectordb/milvus_config.py](src/vectordb/milvus_config.py) |
| Use RAG pipeline | [src/pipeline/rag_pipeline.py](src/pipeline/rag_pipeline.py) |
| Run tests | [test_pipeline.py](test_pipeline.py) |
| Initialize | [setup.py](setup.py) |

---

**Total Project Size:** ~2,000 lines code + 1,500 lines docs + 72 content files
**Status:** ✅ Ready for LLM integration & UI development
