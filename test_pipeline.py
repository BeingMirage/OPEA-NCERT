"""
Simple Test Script for OPEA RAG Pipeline
Demonstrates how to use the system
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

sys.path.insert(0, str(Path(__file__).parent))

from src.vectordb.milvus_config import setup_chroma
from src.services.embedding_service import get_embedding_service
from src.services.language_router import detect_language, route_query
from src.pipeline.rag_pipeline import create_rag_pipeline


def test_language_detection():
    """Test language detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Language Detection")
    logger.info("=" * 60)
    
    test_queries = [
        "What is photosynthesis?",  # English
        "प्रकाश संश्लेषण क्या है?",  # Hindi
        "ফটোসিন্থেসিস কি?",  # Bengali
    ]
    
    for query in test_queries:
        lang = detect_language(query)
        logger.info(f"Query: {query[:30]}...")
        logger.info(f"  → Language: {lang['lang_name']} ({lang['lang_code']}) - {lang['confidence']:.2%}")


def test_query_routing():
    """Test query analysis and routing"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Query Routing Analysis")
    logger.info("=" * 60)
    
    test_queries = [
        "What is photosynthesis? (Class 7 Science)",
        "Explain the water cycle",
        "Class 8 math: solve for x in 2x + 5 = 15",
    ]
    
    for query in test_queries:
        routing = route_query(query)
        logger.info(f"\nQuery: {query}")
        logger.info(f"  → Detected Grade: {routing['grade']}")
        logger.info(f"  → Detected Subject: {routing['subject']}")
        logger.info(f"  → Strategy: {routing['retrieval_strategy']}")


def test_embedding_service():
    """Test embedding service"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Embedding Service")
    logger.info("=" * 60)
    
    embedding_service = get_embedding_service()
    
    test_text = "What is photosynthesis in plants?"
    logger.info(f"Embedding: '{test_text}'")
    
    embedding = embedding_service.embed_text(test_text)
    logger.info(f"✓ Generated embedding with {len(embedding)} dimensions")
    logger.info(f"  Sample values: {embedding[:5]}")


def test_vector_store_connection():
    """Test Chroma vector store connectivity"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Vector Store Connection")
    logger.info("=" * 60)
    
    vector_db = setup_chroma(recreate=False)
    
    if vector_db:
        info = vector_db.get_collection_info()
        logger.info(f"✓ Connected to ChromaDB")
        logger.info(f"  Collection: {info['name']}")
        logger.info(f"  Entities: {info['num_entities']}")
        logger.info(f"  Fields: {info['fields']}")
        return vector_db
    else:
        logger.error("✗ Could not initialize ChromaDB")
        logger.info("Ensure the process has write access to the persistence directory.")
        return None


def test_retrieval(vector_db, embedding_service):
    """Test retrieval capability"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Retrieval from Vector DB")
    logger.info("=" * 60)
    
    if not vector_db or not embedding_service:
        logger.warning("Skipping retrieval test - dependencies not ready")
        return
    
    query = "What is photosynthesis?"
    logger.info(f"Query: {query}")
    
    # Embed query
    query_embedding = embedding_service.embed_text(query)
    
    # Search (without filters first)
    results = vector_db.search_similar(query_embedding, limit=3)
    
    logger.info(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n  {i}. {result['source_file']}")
        logger.info(f"     Grade: {result['grade']}, Subject: {result['subject']}")
        logger.info(f"     Text: {result['text'][:60]}...")


def test_full_pipeline():
    """Test the complete RAG pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Full RAG Pipeline")
    logger.info("=" * 60)
    
    # Setup
    vector_db = setup_chroma(recreate=False)
    embedding_service = get_embedding_service()
    
    if not vector_db or not embedding_service:
        logger.error("Cannot run pipeline - setup failed")
        return
    
    pipeline = create_rag_pipeline(vector_db, embedding_service)
    
    # Process query
    test_query = "What is the water cycle?"
    logger.info(f"Processing: {test_query}")
    
    response = pipeline.process_query(test_query, user_grade="6")
    
    logger.info("\nResponse Summary:")
    logger.info(f"  Status: {response['status']}")
    logger.info(f"  Language: {response['language']['lang_name']}")
    logger.info(f"  Grade: {response['grade']}")
    logger.info(f"  Subject: {response['subject']}")
    logger.info(f"  Sources: {response['num_sources']}")
    
    if response['num_sources'] > 0:
        logger.info("\nFirst source:")
        logger.info(f"  {response['citations'][0]['source']}")


def run_all_tests():
    """Run all tests"""
    logger.info("\n\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 68 + "║")
    logger.info("║" + "OPEA RAG PIPELINE - TEST SUITE".center(68) + "║")
    logger.info("║" + " " * 68 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    
    # Run tests
    test_language_detection()
    test_query_routing()
    test_embedding_service()
    vector_db = test_vector_store_connection()
    
    if vector_db:
        embedding_service = get_embedding_service()
        test_retrieval(vector_db, embedding_service)
        test_full_pipeline()
    
    logger.info("\n\n✓ Test suite complete!")


if __name__ == "__main__":
    run_all_tests()
