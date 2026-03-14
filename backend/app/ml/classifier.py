"""
Text classification module using scikit-learn LogisticRegression.
Provides modular interface for training and prediction.
Can be replaced with other models while maintaining the same interface.
"""

import pickle
import os
import logging
from typing import Tuple, Optional, List
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import dump, load
import numpy as np

logger = logging.getLogger(__name__)

# Default model paths
DEFAULT_MODEL_DIR = os.getenv("MODEL_DIR", "./models")
DEFAULT_VECTORIZER_PATH = os.path.join(DEFAULT_MODEL_DIR, "tfidf_vectorizer.pkl")
DEFAULT_CLASSIFIER_PATH = os.path.join(DEFAULT_MODEL_DIR, "sklearn_classifier.pkl")


class TextClassifier:
    """
    Modular text classifier using scikit-learn LogisticRegression.
    Handles both training and inference.
    """
    
    def __init__(self, categories: List[str] = None):
        """
        Initialize the text classifier.
        
        Args:
            categories: List of valid categories. If provided, classifier will validate predictions.
        """
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        self.classifier = LogisticRegression(
            max_iter=200,
            random_state=42,
            multi_class='multinomial',
            solver='lbfgs'
        )
        
        self.categories = categories
        self.is_trained = False
        logger.info("TextClassifier initialized")
    
    def train(
        self,
        texts: List[str],
        labels: List[str],
        save_model: bool = False,
        model_dir: str = DEFAULT_MODEL_DIR
    ) -> dict:
        """
        Train the classifier on provided texts and labels.
        
        Args:
            texts: List of training texts
            labels: List of corresponding labels/categories
            save_model: Whether to save the model after training
            model_dir: Directory to save models
            
        Returns:
            Dictionary with training statistics
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        if len(set(labels)) < 2:
            raise ValueError("At least 2 different categories required for training")
        
        try:
            logger.info(f"Training classifier with {len(texts)} samples")
            
            # Fit vectorizer and transform texts
            X = self.vectorizer.fit_transform(texts)
            
            # Train classifier
            self.classifier.fit(X, labels)
            self.is_trained = True
            
            # Store categories from training data
            self.categories = list(self.classifier.classes_)
            
            # Calculate training accuracy
            train_accuracy = self.classifier.score(X, labels)
            
            result = {
                "status": "success",
                "samples_trained": len(texts),
                "categories": self.categories,
                "training_accuracy": round(train_accuracy, 4),
                "model_saved": False
            }
            
            if save_model:
                self._save_models(model_dir)
                result["model_saved"] = True
                result["model_dir"] = model_dir
            
            logger.info(f"Training complete. Accuracy: {train_accuracy:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, complaint_text: str) -> dict:
        """
        Predict the category and confidence for a given text.
        
        Args:
            complaint_text: The text to classify
            
        Returns:
            Dictionary with predicted category, confidence score, and probabilities
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        if not complaint_text or not complaint_text.strip():
            return {
                "error": "Empty text provided",
                "predicted_category": None,
                "confidence_score": 0.0
            }
        
        try:
            # Transform text
            X = self.vectorizer.transform([complaint_text])
            
            # Get prediction
            prediction = self.classifier.predict(X)[0]
            
            # Get probability for all classes
            probabilities = self.classifier.predict_proba(X)[0]
            confidence = float(np.max(probabilities))
            
            # Get probabilities for each category
            category_probabilities = {
                cat: round(float(prob), 4)
                for cat, prob in zip(self.classifier.classes_, probabilities)
            }
            
            return {
                "predicted_category": prediction,
                "confidence_score": round(confidence, 4),
                "category_probabilities": category_probabilities,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                "error": str(e),
                "predicted_category": None,
                "confidence_score": 0.0
            }
    
    def predict_batch(self, complaint_texts: List[str]) -> List[dict]:
        """
        Predict categories for multiple texts.
        
        Args:
            complaint_texts: List of texts to classify
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        results = []
        for complaint_text in complaint_texts:
            results.append(self.predict(complaint_text))
        return results
    
    def save_models(self, model_dir: str = DEFAULT_MODEL_DIR) -> bool:
        """
        Save the trained models to disk.
        
        Args:
            model_dir: Directory to save models
            
        Returns:
            True if successful, False otherwise
        """
        return self._save_models(model_dir)
    
    def _save_models(self, model_dir: str) -> bool:
        """Internal method to save models."""
        try:
            os.makedirs(model_dir, exist_ok=True)
            
            # Save vectorizer
            vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
            dump(self.vectorizer, vectorizer_path)
            logger.info(f"Vectorizer saved to {vectorizer_path}")
            
            # Save classifier
            classifier_path = os.path.join(model_dir, "sklearn_classifier.pkl")
            dump(self.classifier, classifier_path)
            logger.info(f"Classifier saved to {classifier_path}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    @staticmethod
    def load_models(model_dir: str = DEFAULT_MODEL_DIR) -> 'TextClassifier':
        """
        Load a trained classifier and vectorizer from disk.
        
        Args:
            model_dir: Directory containing saved models
            
        Returns:
            TextClassifier instance with loaded models
        """
        try:
            vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
            classifier_path = os.path.join(model_dir, "sklearn_classifier.pkl")
            
            # Check if files exist
            if not os.path.exists(vectorizer_path) or not os.path.exists(classifier_path):
                raise FileNotFoundError(
                    f"Model files not found in {model_dir}. "
                    f"Expected: {vectorizer_path}, {classifier_path}"
                )
            
            # Create classifier instance
            classifier_obj = TextClassifier()
            
            # Load models
            classifier_obj.vectorizer = load(vectorizer_path)
            classifier_obj.classifier = load(classifier_path)
            classifier_obj.is_trained = True
            classifier_obj.categories = list(classifier_obj.classifier.classes_)
            
            logger.info(f"Models loaded from {model_dir}")
            return classifier_obj
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def get_info(self) -> dict:
        """
        Get information about the trained classifier.
        
        Returns:
            Dictionary with model information
        """
        return {
            "is_trained": self.is_trained,
            "categories": self.categories,
            "num_features": self.vectorizer.n_features_ if self.is_trained else 0,
            "classifier_type": "LogisticRegression",
            "max_iter": self.classifier.max_iter
        }


# Convenience functions for simple usage
_default_classifier = None


def train(texts: List[str], labels: List[str], categories: List[str] = None) -> dict:
    """
    Train a text classifier with the given texts and labels.
    
    Args:
        texts: List of training texts
        labels: List of corresponding labels
        categories: List of valid categories
        
    Returns:
        Training result dictionary
    """
    global _default_classifier
    _default_classifier = TextClassifier(categories=categories)
    return _default_classifier.train(texts, labels, save_model=False)


def predict(complaint_text: str) -> dict:
    """
    Predict category and confidence for a text.
    
    Args:
        complaint_text: Text to classify
        
    Returns:
        Prediction dictionary with category and confidence
    """
    if _default_classifier is None:
        raise RuntimeError("No classifier trained. Call train() first.")
    return _default_classifier.predict(complaint_text)
