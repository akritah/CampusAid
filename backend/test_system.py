"""
SYSTEM TEST SCRIPT
==================
Quick test to verify all components are working correctly.

Run this after training the model to ensure everything is set up properly.
"""

import os
import sys

# Add backend to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from app.ml.multilingual_embedder import MultilingualEmbedder
from app.ml.complaint_classifier import ComplaintClassifier


def test_embedder():
    """Test multilingual embedder"""
    print("\n" + "=" * 70)
    print("TEST 1: MULTILINGUAL EMBEDDER")
    print("=" * 70)
    
    try:
        embedder = MultilingualEmbedder()
        
        # Test single text
        text = "Hot water not available"
        embedding = embedder.encode(text)
        print(f"✅ Single text encoding works")
        print(f"   Input: '{text}'")
        print(f"   Output shape: {embedding.shape}")
        
        # Test batch encoding
        texts = [
            "Hot water not available",
            "Hot water nahi available",
            "WiFi not working"
        ]
        embeddings = embedder.batch_encode(texts)
        print(f"\n✅ Batch encoding works")
        print(f"   Input: {len(texts)} texts")
        print(f"   Output shape: {embeddings.shape}")
        
        # Test similarity
        sim = embedder.similarity(texts[0], texts[1])
        print(f"\n✅ Similarity calculation works")
        print(f"   '{texts[0]}' vs '{texts[1]}'")
        print(f"   Similarity: {sim:.3f} (should be high ~0.8-0.9)")
        
        return True
    except Exception as e:
        print(f"❌ Embedder test failed: {e}")
        return False


def test_classifier():
    """Test complaint classifier"""
    print("\n" + "=" * 70)
    print("TEST 2: COMPLAINT CLASSIFIER")
    print("=" * 70)
    
    try:
        # Check if model exists
        model_path = os.path.join(SCRIPT_DIR, "models", "complaint_classifier.pkl")
        if not os.path.exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            print("   Please run: python train_classifier.py")
            return False
        
        # Load classifier
        embedder = MultilingualEmbedder()
        classifier = ComplaintClassifier(embedder=embedder)
        classifier.load(model_path)
        print(f"✅ Model loaded successfully")
        print(f"   Categories: {', '.join(classifier.categories)}")
        
        # Test predictions
        test_cases = [
            ("Hot water not available in hostel", "Hostel"),
            ("WiFi nahi chal raha", "IT"),
            ("Teacher class nahi lete", "Academic"),
            ("Electricity issue in classroom", "Infrastructure"),
            ("Fee receipt not updated", "Administration"),
        ]
        
        print(f"\n✅ Testing predictions:")
        correct = 0
        for text, expected_category in test_cases:
            result = classifier.predict(text)
            is_correct = result['predicted_category'] == expected_category
            correct += is_correct
            
            status = "✓" if is_correct else "✗"
            print(f"   {status} '{text}'")
            print(f"      → Predicted: {result['predicted_category']} (confidence: {result['confidence_score']:.2%})")
            if not is_correct:
                print(f"      → Expected: {expected_category}")
        
        accuracy = correct / len(test_cases)
        print(f"\n   Accuracy on test cases: {accuracy:.0%} ({correct}/{len(test_cases)})")
        
        return True
    except Exception as e:
        print(f"❌ Classifier test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_imports():
    """Test that API can import all modules"""
    print("\n" + "=" * 70)
    print("TEST 3: API IMPORTS")
    print("=" * 70)
    
    try:
        from app.main import app
        print("✅ FastAPI app imports successfully")
        
        # Check if model path is correct
        from app.main import MODEL_PATH
        print(f"✅ Model path configured: {MODEL_PATH}")
        
        if os.path.exists(MODEL_PATH):
            print(f"✅ Model file exists")
        else:
            print(f"⚠️ Model file not found (run training first)")
        
        return True
    except Exception as e:
        print(f"❌ API import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CAMPUSAID - SYSTEM TEST")
    print("=" * 70)
    print("This will test all components to ensure everything is working.")
    print("=" * 70)
    
    results = []
    
    # Test 1: Embedder
    results.append(("Embedder", test_embedder()))
    
    # Test 2: Classifier
    results.append(("Classifier", test_classifier()))
    
    # Test 3: API Imports
    results.append(("API Imports", test_api_imports()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou can now:")
        print("1. Start the backend: python -m uvicorn app.main:app --reload")
        print("2. Open frontend: frontend/index.html")
        print("3. Test the system end-to-end")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("Common fixes:")
        print("- Run: python train_classifier.py")
        print("- Check: pip install -r requirements.txt")
    
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
