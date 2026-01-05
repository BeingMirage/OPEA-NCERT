"""
OPEA-based RAG Pipeline
Main orchestrator combining retrieval + generation for doubt-solving
"""

from loguru import logger
from typing import List, Dict
from datetime import datetime

from src.vectordb.milvus_config import ChromaVectorDB
from src.services.embedding_service import EmbeddingService
from src.services.language_router import LanguageRouter


# ============================================
# RAG PIPELINE
# ============================================


class OPEARAGPipeline:
    """
    Main OPEA RAG Pipeline for NCERT Doubt-Solver
    
    Flow:
    1. Query → Language Router (detect language, grade, subject)
    2. Query → Embedding Service (convert to vector)
    3. Vector → Chroma Retriever (find similar chunks with filters)
    4. Chunks → Format for LLM (add metadata, citations)
    5. Context + Query → LLM (generate answer)
    6. Output → Format with citations
    """
    
    def __init__(self, 
                 vector_db: ChromaVectorDB,
                 embedding_service: EmbeddingService,
                 llm_service=None):
        """
        Initialize RAG pipeline
        
        Args:
            vector_db: Vector database instance
            embedding_service: Embedding service instance
            llm_service: LLM service (optional - implement later)
        """
        self.db = vector_db
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.router = LanguageRouter()
        
        logger.info("✓ OPEA RAG Pipeline initialized")
    
    def retrieve_context(self, query: str, grade: str = None, subject: str = None, 
                        top_k: int = 5) -> List[Dict]:
        """
        RETRIEVAL STEP: Find relevant chunks from vector DB
        
        Args:
            query: User's question
            grade: Optional grade filter
            subject: Optional subject filter
            top_k: Number of top results to return
        
        Returns:
            List of retrieved chunks with relevance scores
        """
        logger.info(f"\n[RETRIEVAL] Searching for relevant chunks...")
        
        # Step 1: Embed the query
        query_embedding = self.embedding_service.embed_text(query)
        if not query_embedding:
            logger.error("Failed to embed query")
            return []
        
        # Step 2: Search ChromaDB with filters
        results = self.db.search_similar(
            query_embedding=query_embedding,
            grade=grade,
            subject=subject,
            limit=top_k
        )
        
        logger.info(f"Found {len(results)} relevant chunks")
        for i, chunk in enumerate(results, 1):
            logger.info(f"  {i}. [{chunk['source_file']}] {chunk['text'][:80]}...")
        
        return results
    
    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        FORMAT STEP: Prepare context for LLM
        
        Args:
            retrieved_chunks: List of retrieved chunks
        
        Returns:
            Formatted context string with citations
        """
        if not retrieved_chunks:
            return ""
        
        context = "RELEVANT CONTEXT:\n" + "=" * 60 + "\n\n"
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            context += f"[Source {i}: {chunk['source_file']}]\n"
            context += f"Grade: {chunk['grade']} | Subject: {chunk['subject']}\n"
            context += f"Language: {chunk['language']}\n"
            context += f"---\n"
            context += f"{chunk['text']}\n\n"
        
        return context
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        GENERATION STEP: Generate answer using LLM
        
        Args:
            query: Original question
            context: Formatted context from retrieval
        
        Returns:
            Generated answer (placeholder until LLM service is implemented)
        """
        logger.info(f"\n[GENERATION] Generating answer...")
        
        if not context:
            return "I don't have enough information to answer this question. Please try asking about NCERT curriculum content."
        
        # TODO: Integrate actual LLM here
        # For now, return template answer
        answer = f"""Based on the NCERT curriculum, here's the answer to your question:

{query}

{context}

Note: This is a placeholder response. Full LLM integration coming in next phase.
"""
        
        return answer
    
    def add_citations(self, answer: str, retrieved_chunks: List[Dict]) -> Dict:
        """
        ADD CITATIONS: Ensure answer includes sources
        
        Args:
            answer: Generated answer
            retrieved_chunks: Chunks used for generation
        
        Returns:
            Answer with citations and metadata
        """
        citations = [
            {
                "source": chunk['source_file'],
                "grade": chunk['grade'],
                "subject": chunk['subject'],
                "excerpt": chunk['text'][:200] + "..."
            }
            for chunk in retrieved_chunks
        ]
        
        return {
            "answer": answer,
            "citations": citations,
            "num_sources": len(citations)
        }
    
    def process_query(self, query: str, user_grade: str = None) -> Dict:
        """
        COMPLETE PIPELINE: Query → Answer
        Orchestrates all steps: routing → retrieval → generation → formatting
        
        Args:
            query: User's question
            user_grade: Optional student grade
        
        Returns:
            Complete response with answer, citations, metadata
        """
        logger.info("\n" + "=" * 60)
        logger.info("OPEA RAG PIPELINE: PROCESSING QUERY")
        logger.info("=" * 60)
        
        timestamp = datetime.now().isoformat()
        
        # STEP 1: ROUTE & ANALYZE
        routing = self.router.route_query(query, user_grade)
        
        # STEP 2: RETRIEVE
        retrieved = self.retrieve_context(
            query=query,
            grade=routing['grade'],
            subject=routing['subject'],
            top_k=5
        )
        
        # STEP 3: FORMAT CONTEXT
        context = self.format_context(retrieved)
        
        # STEP 4: GENERATE
        answer = self.generate_answer(query, context)
        
        # STEP 5: ADD CITATIONS
        response = self.add_citations(answer, retrieved)
        
        # STEP 6: ADD METADATA
        response.update({
            'query': query,
            'language': routing['language'],
            'grade': routing['grade'],
            'subject': routing['subject'],
            'retrieval_strategy': routing['retrieval_strategy'],
            'timestamp': timestamp,
            'status': 'success'
        })
        
        logger.info(f"\n✓ PIPELINE COMPLETE - Answer generated with {len(retrieved)} sources")
        
        return response
    
    def handle_feedback(self, response_id: str, feedback: str, rating: int) -> Dict:
        """
        FEEDBACK LOOP: Capture student feedback
        
        Args:
            response_id: ID of the response
            feedback: Text feedback from student
            rating: Rating (1-5 stars)
        
        Returns:
            Feedback confirmation
        """
        feedback_record = {
            'response_id': response_id,
            'feedback': feedback,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Feedback recorded: {rating}★ - {feedback[:50]}...")
        
        # TODO: Store feedback in database for model improvement
        
        return {
            'status': 'feedback_recorded',
            'record': feedback_record
        }


# ============================================
# PIPELINE FACTORY & QUICK SETUP
# ============================================


def create_rag_pipeline(vector_db: ChromaVectorDB, embedding_service: EmbeddingService) -> OPEARAGPipeline:
    """
    Factory function to create RAG pipeline
    Use this in your main application setup
    """
    pipeline = OPEARAGPipeline(
        vector_db=vector_db,
        embedding_service=embedding_service
    )
    return pipeline


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    # This shows how to use the pipeline
    """
    Example:
    
    from src.vectordb.milvus_config import setup_chroma
    from src.services.embedding_service import get_embedding_service
    from src.pipeline.rag_pipeline import create_rag_pipeline
    
    # Setup
    vector_db = setup_chroma()
    embedding = get_embedding_service()
    pipeline = create_rag_pipeline(vector_db, embedding)
    
    # Use
    response = pipeline.process_query(
        query="What is photosynthesis?",
        user_grade="7"
    )
    
    print(response)
    """
    pass
