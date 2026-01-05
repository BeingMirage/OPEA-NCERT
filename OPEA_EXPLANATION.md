# OPEA (Open Platform for Enterprise AI) - Simple Explanation

## What is OPEA?

OPEA is Intel's open-source framework for building enterprise AI applications. Think of it as a **toolkit with pre-built components** that snap together like LEGO blocks to create AI systems.

## Key Concepts (Simplified)

### 1. **Microservices Architecture**
Instead of one giant application, OPEA breaks everything into small, independent services:
- **Embedding Service**: Converts text to vectors (numbers the AI understands)
- **Retriever Service**: Searches the vector database
- **LLM Service**: Generates answers
- **Rerank Service**: Filters best matches

Each service runs separately and talks to others via REST APIs.

```
[User Question] 
    ↓
[Query Router] → Detects language & grade
    ↓
[Retriever] → Finds relevant chunks from vector DB
    ↓
[Reranker] → Sorts by relevance
    ↓
[LLM] → Generates answer
    ↓
[Response Formatter] → Add citations, format output
```

### 2. **Pipeline Composition**
You define a pipeline (workflow) that connects these services. Example:

```
Question → Embedding → Vector Search → LLM → Answer
```

### 3. **Benefits for Your Project**
- **Scalability**: Each service can be scaled independently
- **Language Support**: Easy to add language detection and routing
- **Modularity**: Replace any service without changing others
- **Containerization**: Each service runs in Docker (isolated environment)

## OPEA Components for Your Project

| Component | Purpose | Our Choice |
|-----------|---------|-----------|
| **Vector Store** | Store embeddings of chunks | Milvus (open-source, fast) |
| **Embedding Model** | Convert text → vectors | sentence-transformers (multilingual) |
| **Retriever** | Find similar chunks | LangChain Retriever |
| **LLM** | Generate answers | Open: Ollama/Llama2 or Cloud: HuggingFace |
| **Reranker** | Sort results by relevance | Cross-encoder model |

## Simple Pipeline Flow for NCERT Doubt-Solver

```
1. PREPARATION PHASE:
   Input: chunks.jsonl files
   ↓
   [Embedding Service] → Convert each chunk to vectors
   ↓
   [Milvus Vector DB] → Store vectors + metadata
   
2. QUERY PHASE:
   Input: Student question
   ↓
   [Language Detector] → English/Hindi/etc?
   ↓
   [Grade Filter] → Which grade is student?
   ↓
   [Embedding Service] → Convert question to vector
   ↓
   [Milvus Retriever] → Find 5 best matching chunks (filtered by grade)
   ↓
   [Reranker] → Keep top 3
   ↓
   [LLM Pipeline] → Generate answer using top 3 chunks
   ↓
   [Formatter] → Add citations + format
   ↓
   Output: Answer with sources
```

## Your Current Status

✅ **Extraction Done** → You have chunks.jsonl files with metadata (grade, subject, language)
⏳ **Next: Vector DB Setup** → Store chunks + create search index
⏳ **Then: LLM Pipeline** → Wire everything together

---

## File Structure We'll Create

```
OPEA-RAG/
├── src/
│   ├── services/
│   │   ├── embedding_service.py       # Convert text → vectors
│   │   ├── retriever_service.py       # Search vector DB
│   │   ├── llm_service.py             # Generate answers
│   │   └── language_router.py         # Detect language & grade
│   ├── vectordb/
│   │   ├── milvus_config.py           # Milvus setup
│   │   └── indexer.py                 # Index chunks into Milvus
│   └── pipeline/
│       ├── rag_pipeline.py            # Connect all services (OPEA style)
│       └── prompt_templates.py        # Answer generation templates
├── docker/
│   ├── Dockerfile.milvus             # Vector DB container
│   ├── Dockerfile.embedding          # Embedding service container
│   └── docker-compose.yml            # Run all services together
└── requirements.txt
```
