"""
TRAINING SCRIPT FOR COMPLAINT CLASSIFIER
=========================================
Purpose: Train the classifier on your dataset and save it

This script:
1. Loads training data from CSV
2. Trains the multilingual classifier
3. Saves the trained model
4. Shows performance metrics

Run this ONCE before starting the backend server.
"""

import pandas as pd
import os
import sys

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Add backend to path
sys.path.insert(0, SCRIPT_DIR)

from app.ml.multilingual_embedder import MultilingualEmbedder
from app.ml.complaint_classifier import ComplaintClassifier


def load_training_data(csv_path: str = None):
    """
    Load training data from CSV file.
    
    Expected CSV format:
    id,text,language,category,source
    1,"Hot water not available",en,Hostel,manual
    2,"WiFi nahi working",hi-en,IT,manual
    ...
    
    Args:
        csv_path: Path to CSV file (if None, uses default location)
    
    Returns:
        texts: List of complaint texts
        labels: List of categories
    """
    # Use default path if not provided
    if csv_path is None:
        csv_path = os.path.join(PROJECT_ROOT, "data", "complaints.csv")
    
    print(f"📂 Loading training data from: {csv_path}")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    print(f"   ✓ Loaded {len(df)} complaints")
    print(f"   ✓ Categories: {df['category'].nunique()}")
    print(f"   ✓ Category distribution:")
    print(df['category'].value_counts().to_string())
    
    # Extract texts and labels
    texts = df['text'].tolist()
    labels = df['category'].tolist()
    
    return texts, labels


def main():
    """
    Main training function.
    """
    print("=" * 70)
    print("CAMPUSAID - COMPLAINT CLASSIFIER TRAINING")
    print("=" * 70)
    
    # Configuration
    DATA_PATH = os.path.join(PROJECT_ROOT, "data", "complaints.csv")
    MODEL_SAVE_PATH = os.path.join(SCRIPT_DIR, "models", "complaint_classifier.pkl")
    CONFIDENCE_THRESHOLD = 0.6  # 60% - adjust based on your needs
    
    print(f"\n📍 Working directory: {SCRIPT_DIR}")
    print(f"📍 Project root: {PROJECT_ROOT}")
    
    # Step 1: Load training data
    print("\n📊 STEP 1: LOADING TRAINING DATA")
    print("-" * 70)
    try:
        texts, labels = load_training_data(DATA_PATH)
    except FileNotFoundError:
        print(f"❌ Error: Training data not found at {DATA_PATH}")
        print("   Please ensure complaints.csv exists in the data/ folder")
        return
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Step 2: Initialize embedder
    print("\n🧠 STEP 2: INITIALIZING MULTILINGUAL EMBEDDER")
    print("-" * 70)
    embedder = MultilingualEmbedder()
    
    # Step 3: Initialize and train classifier
    print("\n🎓 STEP 3: TRAINING CLASSIFIER")
    print("-" * 70)
    classifier = ComplaintClassifier(
        embedder=embedder,
        confidence_threshold=CONFIDENCE_THRESHOLD
    )
    
    # Train the classifier
    results = classifier.train(texts, labels, test_size=0.2)
    
    # Step 4: Save the model
    print("\n💾 STEP 4: SAVING MODEL")
    print("-" * 70)
    classifier.save(MODEL_SAVE_PATH)
    
    # Step 5: Test with sample complaints
    print("\n🧪 STEP 5: TESTING WITH SAMPLE COMPLAINTS")
    print("-" * 70)
    
    test_samples = [
        "Hot water nahi aa raha hostel mein",
        "WiFi bahut slow hai",
        "Teacher class nahi lete properly",
        "Electricity ka problem hai classroom mein",
        "Fee receipt nahi mila",
        "Student ko verbally abuse kiya gaya"
    ]
    
    print("\nTesting predictions:")
    for complaint in test_samples:
        result = classifier.predict(complaint)
        review_flag = "⚠️ NEEDS REVIEW" if result['needs_review'] else "✅ AUTO-APPROVED"
        print(f"\n   📝 '{complaint}'")
        print(f"      → Category: {result['predicted_category']}")
        print(f"      → Confidence: {result['confidence_score']:.2%}")
        print(f"      → Status: {review_flag}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"   Model saved to: {MODEL_SAVE_PATH}")
    print(f"   Accuracy: {results['accuracy']:.2%}")
    print(f"   Categories: {', '.join(results['categories'])}")
    print(f"   Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
    print("\n   Next steps:")
    print("   1. Start the backend server: uvicorn app.main:app --reload")
    print("   2. Test the API endpoints")
    print("   3. Integrate with frontend")
    print("=" * 70)


if __name__ == "__main__":
    main()
