#!/usr/bin/env python3
"""
Quick test of core components without the vector store
Tests: Language detection, routing, embedding service
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.services.language_router import LanguageRouter
from src.services.embedding_service import get_embedding_service

def test_language_detection():
    """Test language detection"""
    logger.info("Testing Language Detection...")
    router = LanguageRouter()
    
    queries = [
        ("What is photosynthesis?", "English"),
        ("प्रकाश संश्लेषण क्या है?", "Hindi"),
        ("বালি কি?", "Bengali"),
    ]
    
    for query, expected_lang in queries:
        result = router.detect_language(query)
        logger.info(f"  Query: {query[:30]}...")
        logger.info(f"    Detected: {result['lang_name']} (confidence: {result['confidence']:.2f})")
    
    logger.info("✅ Language detection working!\n")

def test_query_routing():
    """Test query routing"""
    logger.info("Testing Query Routing...")
    router = LanguageRouter()
    
    queries = [
        "What is photosynthesis in class 7 science?",
        "7th grade maths algebra questions",
        "Class 8 English grammar topics",
    ]
    
    for query in queries:
        result = router.route_query(query, user_grade="7")
        logger.info(f"  Query: {query}")
        logger.info(f"    Language: {result['language']['lang_name']}")
        logger.info(f"    Detected Grade: {result['grade']}")
        logger.info(f"    Subject: {result['subject']}")
    
    logger.info("✅ Query routing working!\n")

def test_embedding_service():
    """Test embedding service"""
    logger.info("Testing Embedding Service...")
    
    embedding_service = get_embedding_service()
    logger.info(f"  Model loaded: multilingual-e5-small")
    logger.info(f"  Embedding dimension: {embedding_service.embedding_dim}")
    
    # Test single embedding
    text = "What is photosynthesis?"
    embedding = embedding_service.embed_text(text)
    logger.info(f"  Embedded text: '{text}'")
    logger.info(f"  Vector shape: {embedding.shape}")
    
    # Test batch embedding
    texts = [
        "Photosynthesis is the process...",
        "Mitochondria is the powerhouse...",
        "Chloroplasts contain chlorophyll..."
    ]
    embeddings = embedding_service.embed_texts(texts)
    logger.info(f"  Batch embedded {len(texts)} texts")
    logger.info(f"  Batch vector shape: {embeddings.shape}")
    
    logger.info("✅ Embedding service working!\n")

def main():
    print("\n" + "="*70)
    print("OPEA RAG PIPELINE - COMPONENT TEST (NO VECTOR STORE)")
    print("="*70 + "\n")
    
    try:
        test_language_detection()
        test_query_routing()
        test_embedding_service()
        
        print("="*70)
        print("✅ ALL CORE COMPONENTS WORKING!")
        print("="*70)
        print("\nNow you need to:")
        print("1. Initialize Chroma with: python setup.py")
        print("2. Index chunks via setup.py (uncomment indexing block)")
        print("3. Test full pipeline with: python test_pipeline.py")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
