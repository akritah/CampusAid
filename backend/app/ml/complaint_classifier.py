"""
COMPLAINT CLASSIFIER MODULE
============================
Purpose: Classify complaints into categories (Hostel, Academic, IT, etc.)

HOW IT WORKS:
1. Text → Embeddings (using multilingual_embedder.py)
2. Embeddings → Category (using trained classifier)

WHY TRAIN A CLASSIFIER?
------------------------
The embedding model gives us vectors, but doesn't know our specific categories.
We need to train a simple classifier to map embeddings → categories.

Think of it like:
- Embeddings = Understanding the complaint
- Classifier = Deciding which department should handle it

WHY LOGISTIC REGRESSION?
-------------------------
1. Simple and explainable (important for viva!)
2. Fast training (seconds, not hours)
3. Works well with embeddings
4. Easy to understand the math

Other options: SVM, Random Forest, Neural Network (but more complex)
"""

import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from typing import List, Tuple, Dict
import os

from app.ml.multilingual_embedder import MultilingualEmbedder


class ComplaintClassifier:
    """
    Classifies complaints into categories using embeddings + Logistic Regression.
    
    Categories (examples):
    - Hostel (food, water, cleaning)
    - Academic (syllabus, teaching, exams)
    - IT (WiFi, computers, internet)
    - Infrastructure (electricity, benches, leakage)
    - Harassment (abuse, misconduct, safety)
    - Administration (fees, documents, staff)
    """
    
    def __init__(self, embedder: MultilingualEmbedder = None, confidence_threshold: float = 0.6):
        """
        Initialize the classifier.
        
        Args:
            embedder: MultilingualEmbedder instance (creates new one if None)
            confidence_threshold: Minimum confidence for automatic classification
                                 Below this → Send for manual review
                                 Default: 0.6 (60%)
        """
        # Load or create embedder
        self.embedder = embedder if embedder else MultilingualEmbedder()
        
        # Classifier (will be trained later)
        self.classifier = None
        
        # Category names (will be set during training)
        self.categories = None
        
        # Confidence threshold for manual review
        self.confidence_threshold = confidence_threshold
        
        print(f"✅ Classifier initialized")
        print(f"   Confidence threshold: {confidence_threshold:.0%}")
        print(f"   (Predictions below {confidence_threshold:.0%} will be marked for manual review)")
    
    def train(self, texts: List[str], labels: List[str], test_size: float = 0.2):
        """
        Train the classifier on labeled data.
        
        Args:
            texts: List of complaint texts
            labels: List of corresponding categories
            test_size: Fraction of data to use for testing (default: 20%)
        
        Example:
            >>> texts = [
            ...     "Hot water not available",
            ...     "WiFi not working",
            ...     "Teacher does not explain properly"
            ... ]
            >>> labels = ["Hostel", "IT", "Academic"]
            >>> 
            >>> classifier = ComplaintClassifier()
            >>> classifier.train(texts, labels)
        """
        print(f"\n🎓 TRAINING CLASSIFIER")
        print(f"   Total samples: {len(texts)}")
        print(f"   Unique categories: {len(set(labels))}")
        
        # Step 1: Convert texts to embeddings
        print("\n   Step 1: Generating embeddings...")
        embeddings = self.embedder.batch_encode(texts)
        print(f"   ✓ Generated {len(embeddings)} embeddings")
        
        # Step 2: Split into train and test sets
        print(f"\n   Step 2: Splitting data (train: {(1-test_size)*100:.0f}%, test: {test_size*100:.0f}%)...")
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings, labels,
            test_size=test_size,
            random_state=42,
            stratify=labels  # Ensure balanced split
        )
        print(f"   ✓ Train: {len(X_train)} samples, Test: {len(X_test)} samples")
        
        # Step 3: Train Logistic Regression
        print("\n   Step 3: Training Logistic Regression...")
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            multi_class='multinomial',  # For multiple categories
            solver='lbfgs'  # Good for small datasets
        )
        self.classifier.fit(X_train, y_train)
        print("   ✓ Training complete!")
        
        # Store category names
        self.categories = self.classifier.classes_.tolist()
        
        # Step 4: Evaluate on test set
        print("\n   Step 4: Evaluating on test set...")
        y_pred = self.classifier.predict(X_test)
        accuracy = (y_pred == y_test).mean()
        print(f"   ✓ Accuracy: {accuracy:.2%}")
        
        # Detailed classification report
        print("\n   📊 Detailed Performance:")
        print(classification_report(y_test, y_pred, zero_division=0))
        
        return {
            "accuracy": accuracy,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "categories": self.categories
        }
    
    def predict(self, complaint_text: str) -> Dict:
        """
        Predict category for a single complaint.
        
        Args:
            complaint_text: Complaint text (in Hindi/English/Hinglish)
        
        Returns:
            dict with:
                - predicted_category: Predicted category
                - confidence_score: Confidence score (0 to 1)
                - needs_review: True if confidence < threshold
                - all_probabilities: Probabilities for all categories
        
        Example:
            >>> classifier = ComplaintClassifier()
            >>> # ... train classifier ...
            >>> 
            >>> result = classifier.predict("Hot water nahi aa raha")
            >>> print(result)
            {
                'predicted_category': 'Hostel',
                'confidence_score': 0.87,
                'needs_review': False,
                'all_probabilities': {'Hostel': 0.87, 'IT': 0.05, ...}
            }
        """
        if self.classifier is None:
            raise ValueError("Classifier not trained! Call train() first.")
        
        # Step 1: Convert text to embedding
        embedding = self.embedder.encode(complaint_text).reshape(1, -1)
        
        # Step 2: Predict category
        category = self.classifier.predict(embedding)[0]
        
        # Step 3: Get confidence (probability of predicted category)
        probabilities = self.classifier.predict_proba(embedding)[0]
        confidence = probabilities.max()
        
        # Step 4: Check if manual review needed
        needs_review = confidence < self.confidence_threshold
        
        # Step 5: Get all probabilities
        all_probs = {
            cat: float(prob)
            for cat, prob in zip(self.categories, probabilities)
        }
        
        return {
            "predicted_category": category,
            "confidence_score": float(confidence),
            "needs_review": needs_review,
            "all_probabilities": all_probs,
            "complaint_text": complaint_text
        }
    
    def predict_batch(self, complaint_texts: List[str]) -> List[Dict]:
        """
        Predict categories for multiple complaints.
        
        Args:
            complaint_texts: List of complaint texts
        
        Returns:
            List of prediction dictionaries
        """
        if self.classifier is None:
            raise ValueError("Classifier not trained! Call train() first.")
        
        # Generate embeddings for all texts
        embeddings = self.embedder.batch_encode(complaint_texts)
        
        # Predict categories
        categories = self.classifier.predict(embeddings)
        probabilities = self.classifier.predict_proba(embeddings)
        
        # Build results
        results = []
        for i, complaint_text in enumerate(complaint_texts):
            confidence = probabilities[i].max()
            needs_review = confidence < self.confidence_threshold
            
            all_probs = {
                cat: float(prob)
                for cat, prob in zip(self.categories, probabilities[i])
            }
            
            results.append({
                "predicted_category": categories[i],
                "confidence_score": float(confidence),
                "needs_review": needs_review,
                "all_probabilities": all_probs,
                "complaint_text": complaint_text
            })
        
        return results
    
    def save(self, model_path: str):
        """
        Save trained classifier to disk.
        
        Args:
            model_path: Path to save the model (e.g., 'models/classifier.pkl')
        """
        if self.classifier is None:
            raise ValueError("No trained classifier to save!")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save classifier and metadata
        model_data = {
            "classifier": self.classifier,
            "categories": self.categories,
            "confidence_threshold": self.confidence_threshold
        }
        
        joblib.dump(model_data, model_path)
        print(f"✅ Model saved to: {model_path}")
    
    def load(self, model_path: str):
        """
        Load trained classifier from disk.
        
        Args:
            model_path: Path to saved model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load classifier and metadata
        model_data = joblib.load(model_path)
        
        self.classifier = model_data["classifier"]
        self.categories = model_data["categories"]
        self.confidence_threshold = model_data.get("confidence_threshold", 0.6)
        
        print(f"✅ Model loaded from: {model_path}")
        print(f"   Categories: {', '.join(self.categories)}")


# Example usage for testing
if __name__ == "__main__":
    """
    HOW TO TEST THIS MODULE:
    
    1. Prepare training data (see train_classifier.py)
    2. Run training
    3. Test predictions
    """
    
    print("=" * 60)
    print("TESTING COMPLAINT CLASSIFIER")
    print("=" * 60)
    
    # Sample training data
    texts = [
        "Hot water not available in hostel",
        "Hot water nahi aa raha",
        "Hostel food quality is poor",
        "WiFi not working",
        "Computer lab systems are slow",
        "Internet nahi chal raha",
        "Teacher does not explain properly",
        "Syllabus not completed on time",
        "Teacher behaves rudely",
        "Electricity issue in classroom",
        "Broken benches in lecture hall"
    ]
    
    labels = [
        "Hostel", "Hostel", "Hostel",
        "IT", "IT", "IT",
        "Academic", "Academic",
        "Harassment",
        "Infrastructure", "Infrastructure"
    ]
    
    # Train classifier
    classifier = ComplaintClassifier(confidence_threshold=0.6)
    results = classifier.train(texts, labels)
    
    # Test predictions
    print("\n" + "=" * 60)
    print("TESTING PREDICTIONS")
    print("=" * 60)
    
    test_complaints = [
        "Garam pani nahi mil raha hostel mein",  # Hindi/Hinglish
        "WiFi connection bahut slow hai",  # Hinglish
        "Professor class nahi lete properly"  # Hinglish
    ]
    
    for complaint in test_complaints:
        result = classifier.predict(complaint)
        print(f"\n📝 Complaint: '{complaint}'")
        print(f"   Category: {result['predicted_category']}")
        print(f"   Confidence: {result['confidence_score']:.2%}")
        print(f"   Needs Review: {'⚠️ YES' if result['needs_review'] else '✅ NO'}")
    
    print("\n✅ Classifier working correctly!")
