"""
OPEA Indexing Service
Loads chunks from chunks.jsonl files and indexes them into the vector store.
"""

import json
from pathlib import Path
from loguru import logger
from typing import List, Dict
import glob

from src.vectordb.milvus_config import ChromaVectorDB
from src.services.embedding_service import EmbeddingService, embed_chunks_batch


# ============================================
# CHUNK LOADER
# ============================================


class ChunkLoader:
    """Load chunks from chunks.jsonl files"""
    
    @staticmethod
    def load_chunks_from_file(filepath: str) -> List[Dict]:
        """
        Load chunks from a single chunks.jsonl file
        
        Args:
            filepath: Path to chunks.jsonl file
        
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunk = json.loads(line)
                        chunks.append(chunk)
            logger.info(f"Loaded {len(chunks)} chunks from {Path(filepath).name}")
            return chunks
        except Exception as e:
            logger.error(f"Failed to load chunks from {filepath}: {e}")
            return []
    
    @staticmethod
    def load_all_chunks(root_dir: str = "output", grade_filter=None, subject_filter=None) -> List[Dict]:
        """
        Load all chunks from output directory
        
        Args:
            root_dir: Root directory containing organized chunks
            grade_filter: Optional - only load specific grade(s) e.g., "5" or ["5", "6"]
            subject_filter: Optional - only load specific subject(s)
        
        Returns:
            Combined list of all chunks
        """
        all_chunks = []
        
        # Find all chunks.jsonl files
        pattern = str(Path(root_dir) / "**" / "chunks.jsonl")
        files = glob.glob(pattern, recursive=True)
        
        logger.info(f"Found {len(files)} chunks.jsonl files")
        
        for filepath in files:
            chunks = ChunkLoader.load_chunks_from_file(filepath)
            
            # Apply filters
            if grade_filter:
                if isinstance(grade_filter, str):
                    grade_filter = [grade_filter]
                chunks = [c for c in chunks if c.get("grade") in grade_filter]
            
            if subject_filter:
                if isinstance(subject_filter, str):
                    subject_filter = [subject_filter]
                chunks = [c for c in chunks if c.get("subject") in subject_filter]
            
            all_chunks.extend(chunks)
        
        logger.info(f"✓ Loaded total {len(all_chunks)} chunks (after filters)")
        return all_chunks


# ============================================
# INDEXER SERVICE
# ============================================


class OPEAIndexer:
    """
    OPEA-compatible Indexing Service
    Orchestrates loading chunks, embedding them, and indexing into ChromaDB
    """
    
    def __init__(self, vector_db: ChromaVectorDB, embedding_service: EmbeddingService):
        """
        Initialize indexer
        
        Args:
            vector_db: ChromaVectorDB instance
            embedding_service: EmbeddingService instance
        """
        self.db = vector_db
        self.embedding_service = embedding_service
    
    def index_chunks(self, chunks: List[Dict], batch_size: int = 100) -> int:
        """
        Embed and index chunks into the vector database
        
        Args:
            chunks: List of chunk dictionaries
            batch_size: Process embeddings in batches
        
        Returns:
            Number of successfully indexed chunks
        """
        total_indexed = 0
        
        # Process in batches to avoid memory overload
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} chunks)...")
            
            # Embed batch
            chunks_with_embeddings = embed_chunks_batch(batch, self.embedding_service)
            
            # Index into ChromaDB
            indexed = self.db.insert_chunks(chunks_with_embeddings)
            total_indexed += indexed
            
            logger.info(f"Batch indexed. Progress: {total_indexed}/{len(chunks)}")
        
        logger.info(f"✓ Total indexed: {total_indexed} chunks")
        return total_indexed
    
    def full_pipeline(self, root_dir: str = "output", grade_filter=None, subject_filter=None, batch_size: int = 100):
        """
        Complete indexing pipeline: Load → Embed → Index
        
        Args:
            root_dir: Root directory with chunks
            grade_filter: Grade filter
            subject_filter: Subject filter
            batch_size: Batch size for embedding
        
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 60)
        logger.info("STARTING OPEA INDEXING PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Load chunks
        logger.info("\n[STEP 1] Loading chunks from files...")
        chunks = ChunkLoader.load_all_chunks(
            root_dir=root_dir,
            grade_filter=grade_filter,
            subject_filter=subject_filter
        )
        
        if not chunks:
            logger.error("No chunks loaded. Aborting.")
            return {"status": "failed", "reason": "No chunks loaded"}
        
        # Step 2: Embed and index
        logger.info("\n[STEP 2] Embedding and indexing chunks...")
        indexed_count = self.index_chunks(chunks, batch_size=batch_size)
        
        # Step 3: Verify
        logger.info("\n[STEP 3] Verifying indexing...")
        db_info = self.db.get_collection_info()
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Collection: {db_info['name']}")
        logger.info(f"Total entities: {db_info['num_entities']}")
        
        return {
            "status": "success",
            "chunks_loaded": len(chunks),
            "chunks_indexed": indexed_count,
            "collection_info": db_info
        }


# ============================================
# QUICK SETUP FUNCTION
# ============================================


def index_all_chunks(vector_db: ChromaVectorDB, embedding_service: EmbeddingService, 
                     root_dir: str = "output", grade_filter=None, subject_filter=None):
    """
    Quick function to index all chunks
    Use this in your main pipeline setup
    """
    indexer = OPEAIndexer(vector_db, embedding_service)
    result = indexer.full_pipeline(
        root_dir=root_dir,
        grade_filter=grade_filter,
        subject_filter=subject_filter
    )
    return result
