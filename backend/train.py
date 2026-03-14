"""
Training script for the complaint classifier.

Usage:
    python train.py --complaints-csv ../data/complaints.csv --labels-csv ../data/labels.csv
    python train.py  # Uses default paths
"""

import sys
import os
import argparse
import logging
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml.classifier import TextClassifier
from app.ml.embedder import get_embedding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_COMPLAINTS_CSV = "../data/complaints.csv"
DEFAULT_LABELS_CSV = "../data/labels.csv"
DEFAULT_MODEL_DIR = "./models"


def load_training_data(complaints_csv: str, labels_csv: str) -> tuple:
    """
    Load complaint text and labels from CSV files.
    
    Args:
        complaints_csv: Path to complaints CSV file
        labels_csv: Path to labels CSV file
        
    Returns:
        Tuple of (texts, labels)
    """
    try:
        logger.info(f"Loading complaints from {complaints_csv}")
        complaints_df = pd.read_csv(complaints_csv)
        
        logger.info(f"Loading labels from {labels_csv}")
        labels_df = pd.read_csv(labels_csv)
        
        # Extract texts and labels
        if 'text' in complaints_df.columns:
            texts = complaints_df['text'].tolist()
        elif 'complaint' in complaints_df.columns:
            texts = complaints_df['complaint'].tolist()
        else:
            # Use first column if no standard column name
            texts = complaints_df.iloc[:, 0].tolist()
        
        if 'category' in labels_df.columns:
            labels = labels_df['category'].tolist()
        elif 'label' in labels_df.columns:
            labels = labels_df['label'].tolist()
        else:
            # Use first column if no standard column name
            labels = labels_df.iloc[:, 0].tolist()
        
        logger.info(f"Loaded {len(texts)} complaints and {len(labels)} labels")
        
        if len(texts) != len(labels):
            raise ValueError(f"Mismatch: {len(texts)} texts vs {len(labels)} labels")
        
        return texts, labels
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def generate_embeddings(texts: list, save_path: str = None) -> list:
    """
    Generate multilingual embeddings for all texts.
    
    Args:
        texts: List of complaint texts
        save_path: Optional path to save embeddings as numpy file
        
    Returns:
        List of embeddings
    """
    logger.info(f"Generating embeddings for {len(texts)} texts...")
    embeddings = []
    
    for i, text in enumerate(texts):
        if (i + 1) % 10 == 0:
            logger.info(f"  Processed {i + 1}/{len(texts)} texts")
        
        embedding = get_embedding(text)
        if embedding is None:
            logger.warning(f"Failed to generate embedding for text {i}: {text[:50]}...")
            # Use zero embedding as fallback
            embedding = [0.0] * 768
        
        embeddings.append(embedding)
    
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    if save_path:
        np.save(save_path, np.array(embeddings))
        logger.info(f"Embeddings saved to {save_path}")
    
    return embeddings


def train_classifier(
    texts: list,
    labels: list,
    test_size: float = 0.2,
    model_dir: str = DEFAULT_MODEL_DIR
) -> dict:
    """
    Train the classifier on complaint texts and labels.
    
    Args:
        texts: List of complaint texts
        labels: List of corresponding category labels
        test_size: Fraction of data to use for testing (default: 0.2)
        model_dir: Directory to save trained models
        
    Returns:
        Dictionary with training results
    """
    logger.info("="*70)
    logger.info("COMPLAINT CLASSIFIER TRAINING")
    logger.info("="*70)
    
    # Data statistics
    unique_categories = set(labels)
    logger.info(f"Total samples: {len(texts)}")
    logger.info(f"Unique categories: {len(unique_categories)}")
    logger.info(f"Categories: {', '.join(sorted(unique_categories))}")
    
    # Category distribution
    logger.info("\nCategory distribution:")
    category_counts = {}
    for label in labels:
        category_counts[label] = category_counts.get(label, 0) + 1
    
    for cat in sorted(category_counts.keys()):
        count = category_counts[cat]
        percentage = (count / len(labels)) * 100
        logger.info(f"  {cat}: {count} ({percentage:.1f}%)")
    
    # Split data
    logger.info(f"\nSplitting data: {(1-test_size)*100:.0f}% train, {test_size*100:.0f}% test")
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=test_size,
        random_state=42,
        stratify=labels  # Maintain class distribution
    )
    
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Test samples: {len(X_test)}")
    
    # Train classifier
    logger.info("\nTraining classifier...")
    classifier = TextClassifier(categories=list(unique_categories))
    
    train_result = classifier.train(
        X_train,
        y_train,
        save_model=False
    )
    
    logger.info(f"Training accuracy: {train_result['training_accuracy']:.4f}")
    
    # Evaluate on test set
    logger.info("\nEvaluating on test set...")
    test_predictions = []
    
    for i, text in enumerate(X_test):
        if (i + 1) % 10 == 0:
            logger.info(f"  Evaluated {i + 1}/{len(X_test)} test samples")
        
        prediction = classifier.predict(text)
        test_predictions.append(prediction['predicted_category'])
    
    # Calculate metrics
    test_accuracy = accuracy_score(y_test, test_predictions)
    logger.info(f"Test accuracy: {test_accuracy:.4f}")
    
    # Confusion matrix
    logger.info("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, test_predictions, labels=sorted(unique_categories))
    
    # Print confusion matrix with headers
    categories_sorted = sorted(unique_categories)
    logger.info("\nConfusion Matrix (rows=actual, columns=predicted):")
    
    # Header
    header = "          " + "".join(f"{cat[:8]:>10}" for cat in categories_sorted)
    logger.info(header)
    logger.info("-" * len(header))
    
    # Rows
    for i, actual_cat in enumerate(categories_sorted):
        row = f"{actual_cat[:9]:>9} " + "".join(f"{cm[i][j]:>10}" for j in range(len(categories_sorted)))
        logger.info(row)
    
    # Classification report
    logger.info("\nClassification Report:")
    report = classification_report(
        y_test,
        test_predictions,
        labels=categories_sorted,
        digits=4
    )
    logger.info("\n" + report)
    
    # Save models
    logger.info("\nSaving trained models...")
    classifier.save_models(model_dir)
    logger.info(f"Models saved to {model_dir}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("TRAINING SUMMARY")
    logger.info("="*70)
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Test samples: {len(X_test)}")
    logger.info(f"Training accuracy: {train_result['training_accuracy']:.4f}")
    logger.info(f"Test accuracy: {test_accuracy:.4f}")
    logger.info(f"Model saved to: {model_dir}")
    logger.info("="*70 + "\n")
    
    return {
        "training_accuracy": train_result['training_accuracy'],
        "test_accuracy": test_accuracy,
        "confusion_matrix": cm,
        "categories": categories_sorted,
        "model_dir": model_dir
    }


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(
        description="Train the complaint classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train.py
  python train.py --complaints-csv ../data/complaints.csv --labels-csv ../data/labels.csv
  python train.py --model-dir ./trained_models --test-size 0.3
        """
    )
    
    parser.add_argument(
        "--complaints-csv",
        type=str,
        default=DEFAULT_COMPLAINTS_CSV,
        help=f"Path to complaints CSV file (default: {DEFAULT_COMPLAINTS_CSV})"
    )
    parser.add_argument(
        "--labels-csv",
        type=str,
        default=DEFAULT_LABELS_CSV,
        help=f"Path to labels CSV file (default: {DEFAULT_LABELS_CSV})"
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default=DEFAULT_MODEL_DIR,
        help=f"Directory to save trained models (default: {DEFAULT_MODEL_DIR})"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data to use for testing (default: 0.2)"
    )
    parser.add_argument(
        "--embeddings-cache",
        type=str,
        default=None,
        help="Optional path to save generated embeddings as numpy file"
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        texts, labels = load_training_data(args.complaints_csv, args.labels_csv)
        
        # Train classifier
        results = train_classifier(
            texts,
            labels,
            test_size=args.test_size,
            model_dir=args.model_dir
        )
        
        logger.info("Training completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
