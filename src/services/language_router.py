"""
OPEA Language Router Service
Detects query language and grade level for intelligent routing
"""

from langdetect import detect, detect_langs
from loguru import logger
from typing import Dict, List


# ============================================
# LANGUAGE MAPPINGS
# ============================================

LANGUAGE_CODES = {
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'ur': 'Urdu',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'as': 'Assamese',
    'or': 'Odia',
    'sa': 'Sanskrit',
}

# Grade levels available in our dataset
AVAILABLE_GRADES = ["5", "6", "7", "8"]

# Subjects available
AVAILABLE_SUBJECTS = [
    "English", "Hindi", "Maths", "Science", 
    "Social Science", "Sanskrit", "Urdu", "Arts", 
    "Physical Education", "Vocational Education"
]


class LanguageRouter:
    """
    OPEA-style Language Detection and Query Router
    Analyzes incoming queries to determine:
    1. Language of query
    2. Student's intended grade
    3. Best retrieval strategy
    """
    
    @staticmethod
    def detect_language(text: str) -> Dict:
        """
        Detect the language of input text
        
        Args:
            text: Input query text
        
        Returns:
            Dict with language info:
            {
                'lang_code': 'en',
                'lang_name': 'English',
                'confidence': 0.95
            }
        """
        try:
            # Get all detected languages with probabilities
            lang_probs = detect_langs(text)
            
            if not lang_probs:
                return {
                    'lang_code': 'en',
                    'lang_name': 'English',
                    'confidence': 0.0,
                    'note': 'Could not detect language, defaulting to English'
                }
            
            # Top detected language
            detected = lang_probs[0]
            lang_code = detected.lang
            confidence = detected.prob
            
            lang_name = LANGUAGE_CODES.get(lang_code, lang_code.upper())
            
            logger.info(f"Language detected: {lang_name} ({lang_code}) - Confidence: {confidence:.2f}")
            
            return {
                'lang_code': lang_code,
                'lang_name': lang_name,
                'confidence': confidence,
                'alternatives': [
                    {'code': p.lang, 'name': LANGUAGE_CODES.get(p.lang, p.lang.upper()), 'prob': p.prob}
                    for p in lang_probs[1:3]  # Top 2 alternatives
                ]
            }
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                'lang_code': 'en',
                'lang_name': 'English',
                'confidence': 0.0,
                'error': str(e)
            }
    
    @staticmethod
    def extract_grade_from_query(text: str) -> str:
        """
        Try to extract grade mention from query
        e.g., "Class 7 math question" → "7"
        
        Args:
            text: Query text
        
        Returns:
            Grade (5-8) or None if not found
        """
        text_lower = text.lower()
        
        # Look for grade/class mention
        grade_indicators = [
            ("class 5", "5"), ("grade 5", "5"), ("class-5", "5"),
            ("class 6", "6"), ("grade 6", "6"), ("class-6", "6"),
            ("class 7", "7"), ("grade 7", "7"), ("class-7", "7"),
            ("class 8", "8"), ("grade 8", "8"), ("class-8", "8"),
        ]
        
        for indicator, grade in grade_indicators:
            if indicator in text_lower:
                logger.info(f"Grade detected from query: {grade}")
                return grade
        
        return None
    
    @staticmethod
    def extract_subject_from_query(text: str) -> str:
        """
        Try to extract subject mention from query
        e.g., "What is photosynthesis?" → "Science"
        
        Args:
            text: Query text
        
        Returns:
            Subject name or None
        """
        text_lower = text.lower()
        
        # Map keywords to subjects
        subject_keywords = {
            "Math": ["math", "maths", "mathematics", "equation", "algebra", "geometry"],
            "Science": ["science", "photosynthesis", "atom", "cell", "chemistry", "physics"],
            "English": ["english", "grammar", "literature", "poem", "essay"],
            "Hindi": ["hindi", "हिंदी"],
            "History": ["history", "historical", "empire", "dynasty"],
            "Geography": ["geography", "map", "country", "state"],
        }
        
        for subject, keywords in subject_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    logger.info(f"Subject detected from query: {subject}")
                    return subject
        
        return None
    
    @staticmethod
    def route_query(query: str, user_grade: str = None) -> Dict:
        """
        Complete query analysis for routing
        
        Args:
            query: User's question
            user_grade: Optional - student's grade if already known
        
        Returns:
            Routing information:
            {
                'language': {...},
                'grade': '5',
                'subject': 'Science',
                'retrieval_strategy': 'grade_filtered',
                'filters': {'grade': '5', 'subject': 'Science'}
            }
        """
        logger.info("\n--- Query Router Analysis ---")
        logger.info(f"Query: {query[:100]}...")
        
        # Detect language
        lang_info = LanguageRouter.detect_language(query)
        
        # Extract or use provided grade
        detected_grade = LanguageRouter.extract_grade_from_query(query)
        grade = user_grade or detected_grade or "5"  # Default to grade 5
        
        if grade not in AVAILABLE_GRADES:
            logger.warning(f"Grade {grade} not available, defaulting to 5")
            grade = "5"
        
        # Extract subject
        subject = LanguageRouter.extract_subject_from_query(query)
        
        # Determine retrieval strategy
        if grade and subject:
            retrieval_strategy = "grade_subject_filtered"
            filters = {"grade": grade, "subject": subject}
        elif grade:
            retrieval_strategy = "grade_filtered"
            filters = {"grade": grade}
        else:
            retrieval_strategy = "global"
            filters = {}
        
        routing_info = {
            'language': lang_info,
            'grade': grade,
            'subject': subject,
            'retrieval_strategy': retrieval_strategy,
            'filters': filters,
            'confidence_score': lang_info['confidence']
        }
        
        logger.info(f"Routing Strategy: {retrieval_strategy}")
        logger.info(f"Filters: {filters}")
        
        return routing_info


# ============================================
# QUICK HELPER FUNCTIONS
# ============================================


def detect_language(query: str) -> Dict:
    """Quick language detection"""
    return LanguageRouter.detect_language(query)


def route_query(query: str, user_grade: str = None) -> Dict:
    """Quick query routing"""
    return LanguageRouter.route_query(query, user_grade)
