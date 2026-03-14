"""
Language detection utility using langdetect library.
"""

from langdetect import detect, detect_langs, LangDetectException
from typing import Tuple


def detect_language(text: str) -> str:
    """
    Detect the language of a given text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Language code (e.g., 'en', 'es', 'fr') or 'unknown' if detection fails
    """
    if not text or not text.strip():
        return "unknown"
    
    try:
        language = detect(text)
        return language
    except LangDetectException:
        return "unknown"
    except Exception:
        return "unknown"


def detect_language_with_confidence(text: str) -> Tuple[str, float]:
    """
    Detect the language of a given text with confidence score.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (language_code, confidence) where confidence is 0.0-1.0
        Returns ('unknown', 0.0) if detection fails
    """
    if not text or not text.strip():
        return "unknown", 0.0
    
    try:
        # detect_langs returns a list of Language objects with probabilities
        probabilities = detect_langs(text)
        
        if probabilities:
            # Get the language with highest probability
            top_lang = probabilities[0]
            return str(top_lang.lang), round(float(top_lang.prob), 2)
        
        return "unknown", 0.0
    except LangDetectException:
        return "unknown", 0.0
    except Exception:
        return "unknown", 0.0


def is_supported_language(language_code: str, supported_codes: list = None) -> bool:
    """
    Check if a language code is in the list of supported languages.
    
    Args:
        language_code: The language code to check
        supported_codes: List of supported language codes (default: ['en', 'es', 'fr', 'de', 'it', 'pt'])
        
    Returns:
        True if supported, False otherwise
    """
    if supported_codes is None:
        supported_codes = ["en", "es", "fr", "de", "it", "pt", "hi", "ta"]
    
    return language_code in supported_codes
