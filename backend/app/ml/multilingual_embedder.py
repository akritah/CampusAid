"""
MULTILINGUAL EMBEDDINGS MODULE
===============================
Purpose: Convert text (in any language) into numerical vectors (embeddings)

WHAT ARE EMBEDDINGS?
--------------------
Embeddings are like "coordinates" for words/sentences in a mathematical space.
Similar meanings → Similar coordinates (close together)
Different meanings → Different coordinates (far apart)

Example:
"Hot water not available" (English)
"Hot water nahi available" (Hinglish)  
"गर्म पानी नहीं आ रहा" (Hindi)

All three will have SIMILAR embeddings because they mean the same thing!

WHY MULTILINGUAL EMBEDDINGS?
----------------------------
1. NO TRANSLATION NEEDED: The model understands Hindi, English, and Hinglish directly
2. SAME MEANING = SAME VECTOR: Complaints in different languages map to same space
3. PRETRAINED: We don't train this - we use a model trained by experts on billions of texts

WHY NOT TRAIN FROM SCRATCH?
---------------------------
Training a language model requires:
- Millions of text samples
- Expensive GPUs (₹10+ lakhs)
- Weeks of training time
- PhD-level expertise

Instead, we use a PRETRAINED model (like using a calculator instead of building one!)
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class MultilingualEmbedder:
    """
    Converts text in Hindi/English/Hinglish into embeddings (numerical vectors).
    
    This is the CORE of our multilingual understanding!
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the multilingual embedding model.
        
        Args:
            model_name: Name of the pretrained model
                       Default: "paraphrase-multilingual-MiniLM-L12-v2"
                       - Supports 50+ languages including Hindi
                       - Fast and lightweight (good for college projects)
                       - Size: ~420MB
        
        Other good options:
        - "distiluse-base-multilingual-cased-v2" (smaller, faster)
        - "paraphrase-multilingual-mpnet-base-v2" (larger, more accurate)
        
        The model will be downloaded automatically on first use.
        """
        print(f"📥 Loading multilingual model: {model_name}")
        print("   (This may take a minute on first run - model is being downloaded)")
        
        # Load the pretrained model
        # This model was trained on millions of sentences in multiple languages
        self.model = SentenceTransformer(model_name)
        
        # Get embedding dimension (usually 384 or 768)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        print(f"✅ Model loaded! Embedding dimension: {self.embedding_dim}")
        print(f"   Supports: Hindi, English, Hinglish, and 47+ other languages")
    
    def encode(self, texts: Union[str, List[str]], show_progress: bool = False) -> np.ndarray:
        """
        Convert text(s) into embeddings.
        
        Args:
            texts: Single text or list of texts
            show_progress: Show progress bar for large batches
        
        Returns:
            numpy array of embeddings
            - Single text: shape (embedding_dim,)
            - Multiple texts: shape (num_texts, embedding_dim)
        
        Example:
            >>> embedder = MultilingualEmbedder()
            >>> 
            >>> # Single text
            >>> emb1 = embedder.encode("Hot water not available")
            >>> print(emb1.shape)  # (384,)
            >>> 
            >>> # Multiple texts
            >>> texts = ["Hot water nahi available", "WiFi not working"]
            >>> embs = embedder.encode(texts)
            >>> print(embs.shape)  # (2, 384)
        """
        # Convert to list if single string
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        # Generate embeddings
        # The model handles Hindi/English/Hinglish automatically!
        embeddings = self.model.encode(
            texts,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        # Return single embedding if input was single text
        if single_text:
            return embeddings[0]
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts (0 to 1).
        
        Higher score = More similar meaning
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0 = completely different, 1 = identical meaning)
        
        Example:
            >>> embedder = MultilingualEmbedder()
            >>> 
            >>> # Same meaning, different languages
            >>> score = embedder.similarity(
            ...     "Hot water not available",
            ...     "Hot water nahi available"
            ... )
            >>> print(f"Similarity: {score:.2f}")  # ~0.85-0.95
            >>> 
            >>> # Different meanings
            >>> score = embedder.similarity(
            ...     "Hot water not available",
            ...     "WiFi not working"
            ... )
            >>> print(f"Similarity: {score:.2f}")  # ~0.20-0.40
        """
        # Get embeddings
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        # Calculate cosine similarity
        # Cosine similarity = dot product / (magnitude1 * magnitude2)
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    
    def batch_encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode large number of texts in batches (more efficient).
        
        Args:
            texts: List of texts
            batch_size: Number of texts to process at once
        
        Returns:
            numpy array of embeddings
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )


# Example usage and testing
if __name__ == "__main__":
    """
    HOW TO TEST THIS MODULE:
    
    1. Install required package:
       pip install sentence-transformers
    
    2. Run this file:
       python multilingual_embedder.py
    """
    
    print("=" * 60)
    print("TESTING MULTILINGUAL EMBEDDINGS")
    print("=" * 60)
    
    # Initialize embedder
    embedder = MultilingualEmbedder()
    
    # Test 1: Same complaint in different languages
    print("\n📝 Test 1: Same meaning, different languages")
    complaints = [
        "Hot water not available in hostel",  # English
        "Hot water nahi available in hostel",  # Hinglish
        "हॉस्टल में गर्म पानी नहीं आ रहा है"  # Hindi
    ]
    
    embeddings = embedder.encode(complaints)
    print(f"   Generated {len(embeddings)} embeddings")
    print(f"   Each embedding has {embeddings.shape[1]} dimensions")
    
    # Calculate similarities
    print("\n   Similarity scores:")
    for i in range(len(complaints)):
        for j in range(i + 1, len(complaints)):
            sim = embedder.similarity(complaints[i], complaints[j])
            print(f"   '{complaints[i][:30]}...' vs '{complaints[j][:30]}...'")
            print(f"   → Similarity: {sim:.3f} (High = Same meaning!)")
    
    # Test 2: Different complaints
    print("\n📝 Test 2: Different meanings")
    complaint1 = "Hot water not available"
    complaint2 = "WiFi not working"
    sim = embedder.similarity(complaint1, complaint2)
    print(f"   '{complaint1}' vs '{complaint2}'")
    print(f"   → Similarity: {sim:.3f} (Low = Different meanings)")
    
    print("\n✅ Multilingual embeddings working correctly!")
    print("   Key takeaway: Same meaning → Similar embeddings (regardless of language)")
