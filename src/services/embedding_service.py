"""
OPEA-style Embedding Service
Converts text to vector embeddings using multilingual models
"""

from sentence_transformers import SentenceTransformer
from loguru import logger
import numpy as np
from typing import List, Union


# ============================================
# EMBEDDING MODEL SELECTION
# ============================================

# Multilingual model - works for English, Hindi, and 100+ languages
# Dimension: 384 (matches our Chroma schema)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/multilingual-e5-small"

# If you need better quality but slower:
# BETTER_MODEL = "sentence-transformers/multilingual-e5-large"  # 1024 dimensions


class EmbeddingService:
    """
    OPEA-compatible Embedding Service
    Converts text to dense vector representations
    """
    
    def __init__(self, model_name=DEFAULT_EMBEDDING_MODEL):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # for e5-small
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✓ Model loaded. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"✗ Failed to load model: {e}")
            raise
    
    def embed_text(self, text: str, normalize=True) -> List[float]:
        """
        Convert a single text to embedding
        
        Args:
            text: Text to embed
            normalize: If True, normalize vector to unit length
        
        Returns:
            List of floats (384 dimensions)
        """
        try:
            if not self.model:
                logger.error("Model not loaded")
                return None
            
            # Encode text
            embedding = self.model.encode(text, normalize_embeddings=normalize)
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return None
    
    def embed_texts(self, texts: List[str], normalize=True, batch_size=32) -> List[List[float]]:
        """
        Convert multiple texts to embeddings (batch processing for efficiency)
        
        Args:
            texts: List of texts to embed
            normalize: If True, normalize vectors
            batch_size: Process in batches for memory efficiency
        
        Returns:
            List of embeddings (each is a list of floats)
        """
        try:
            if not self.model:
                logger.error("Model not loaded")
                return []
            
            logger.info(f"Embedding {len(texts)} texts...")
            embeddings = self.model.encode(texts, normalize_embeddings=normalize, batch_size=batch_size, show_progress_bar=True)
            
            # Convert numpy arrays to lists
            result = [emb.tolist() for emb in embeddings]
            logger.info(f"✓ Embedded {len(result)} texts")
            
            return result
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return []
    
    def get_model_info(self):
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "max_seq_length": self.model.max_seq_length if self.model else None,
        }


# ============================================
# SPECIALIZED EMBEDDING FUNCTIONS FOR OPEA PIPELINE
# ============================================


def embed_chunk(chunk: dict, embedding_service: EmbeddingService) -> dict:
    """
    Embed a single chunk from chunks.jsonl
    
    Args:
        chunk: Dict with 'text' key
        embedding_service: EmbeddingService instance
    
    Returns:
        Original chunk dict + 'embedding' key with vector
    """
    embedding = embedding_service.embed_text(chunk["text"])
    chunk_with_embedding = chunk.copy()
    chunk_with_embedding["embedding"] = embedding
    return chunk_with_embedding


def embed_chunks_batch(chunks: List[dict], embedding_service: EmbeddingService) -> List[dict]:
    """
    Embed multiple chunks efficiently
    
    Args:
        chunks: List of chunk dicts
        embedding_service: EmbeddingService instance
    
    Returns:
        List of chunks with embeddings added
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_service.embed_texts(texts)
    
    result = []
    for chunk, embedding in zip(chunks, embeddings):
        chunk_copy = chunk.copy()
        chunk_copy["embedding"] = embedding
        result.append(chunk_copy)
    
    return result


# ============================================
# INITIALIZATION HELPER
# ============================================


def get_embedding_service(model_name=DEFAULT_EMBEDDING_MODEL) -> EmbeddingService:
    """
    Get or create embedding service (singleton pattern)
    Use in OPEA pipeline to ensure single model instance
    """
    try:
        service = EmbeddingService(model_name)
        return service
    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {e}")
        return None
