"""
Multilingual text embedding module using sentence-transformers.
Supports English, Hindi, and code-mixed text.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Model name - multilingual model supporting 50+ languages
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

# Lazy load the model (only when first needed)
_model = None


def _load_model():
    """Load the sentence-transformer model."""
    global _model
    if _model is None:
        try:
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    return _model


def get_embedding(text: str) -> Union[List[float], None]:
    """
    Generate a multilingual embedding vector for the given text.
    
    Supports:
    - English text
    - Hindi (Devanagari script)
    - Code-mixed text (English + Hindi)
    
    Args:
        text: The text to embed
        
    Returns:
        A list of floats representing the embedding vector (dimension: 768)
        Returns None if embedding generation fails
        
    Example:
        >>> embedding = get_embedding("This is a complaint about the wifi")
        >>> len(embedding)
        768
    """
    if not text or not text.strip():
        logger.warning("Attempted to embed empty text")
        return None
    
    try:
        model = _load_model()
        # Generate embedding
        embedding = model.encode(text, convert_to_tensor=False)
        # Convert to list for JSON serialization
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None


def get_embeddings_batch(texts: List[str]) -> Union[List[List[float]], None]:
    """
    Generate embedding vectors for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors, or None if batch generation fails
        
    Example:
        >>> texts = ["Complaint 1", "Complaint 2"]
        >>> embeddings = get_embeddings_batch(texts)
        >>> len(embeddings)
        2
    """
    if not texts or len(texts) == 0:
        logger.warning("Attempted to embed empty text list")
        return None
    
    try:
        model = _load_model()
        # Generate embeddings in batch (more efficient)
        embeddings = model.encode(texts, convert_to_tensor=False)
        # Convert to list for JSON serialization
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {str(e)}")
        return None


def get_model_info() -> dict:
    """
    Get information about the loaded embedding model.
    
    Returns:
        Dictionary with model details
    """
    try:
        model = _load_model()
        return {
            "model_name": MODEL_NAME,
            "embedding_dimension": model.get_sentence_embedding_dimension(),
            "max_seq_length": model.get_max_seq_length(),
            "languages_supported": [
                "English", "Hindi", "Code-mixed (English-Hindi)",
                "Spanish", "French", "German", "Portuguese",
                "Italian", "Dutch", "Arabic", "Chinese", "Japanese"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return {"error": str(e)}


def similarity(text1: str, text2: str) -> Union[float, None]:
    """
    Calculate cosine similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1, or None if calculation fails
    """
    try:
        embedding1 = get_embedding(text1)
        embedding2 = get_embedding(text2)
        
        if embedding1 is None or embedding2 is None:
            return None
        
        # Convert to numpy arrays for calculation
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity_score = dot_product / (norm1 * norm2)
        return round(float(similarity_score), 4)
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return None
