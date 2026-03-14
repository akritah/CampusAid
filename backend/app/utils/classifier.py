"""
Temporary keyword-based classifier for complaints.
This is a placeholder until ML models are integrated.
"""

from typing import Tuple
from app.utils.categories import CATEGORY_TO_DEPARTMENT, VALID_CATEGORIES


# Keyword mapping for each category
KEYWORD_MAPPING = {
    "IT": [
        "wifi", "internet", "network", "website", "application", "app", "software",
        "email", "server", "connection", "computer", "laptop", "bug", "crash",
        "online", "password", "login", "access", "technical", "system"
    ],
    "Infrastructure": [
        "building", "road", "construction", "facility", "room", "classroom",
        "lab", "furniture", "electricity", "water", "maintenance", "repair",
        "broken", "damaged", "leaking", "plumbing", "ceiling", "wall",
        "parking", "transport", "bus", "vehicle"
    ],
    "Hostel": [
        "hostel", "room", "dormitory", "dorm", "bed", "mess", "food",
        "laundry", "noise", "roommate", "accommodation", "lodging",
        "cleaning", "water", "bathroom", "common room"
    ],
    "Academic": [
        "class", "course", "exam", "grade", "marks", "syllabus", "attendance",
        "professor", "teacher", "lecture", "assignment", "project", "result",
        "graduation", "degree", "curriculum", "tutorial", "practical", "lab"
    ],
    "Harassment": [
        "harassment", "abuse", "bullying", "threat", "assault", "discriminat",
        "inappropriate", "behavior", "conduct", "misconduct", "unwanted",
        "molest", "humiliation", "intimidat", "targeted", "attacked"
    ],
    "Administration": [
        "admission", "registration", "certificate", "document", "form", "fee",
        "payment", "policy", "rule", "regulation", "procedure", "office",
        "staff", "decision", "appeal", "complaint", "verification", "official",
        "records", "transcript", "enrollment"
    ],
}


def keyword_based_classifier(text: str) -> Tuple[str, float]:
    """
    Classify complaint using keyword matching.
    
    Args:
        text: The complaint text to classify
        
    Returns:
        Tuple of (category, confidence) where confidence is between 0.0 and 1.0
    """
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Count keyword matches for each category
    category_scores = {}
    
    for category, keywords in KEYWORD_MAPPING.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        category_scores[category] = matches
    
    # Find the category with the most matches
    if not any(category_scores.values()):
        # No keywords found, return default
        return "Administration", 0.3
    
    best_category = max(category_scores, key=category_scores.get)
    match_count = category_scores[best_category]
    
    # Calculate confidence based on match density
    # More matches = higher confidence
    total_keywords = sum(len(keywords) for keywords in KEYWORD_MAPPING.values())
    confidence = min(0.95, (match_count / len(KEYWORD_MAPPING[best_category])) * 0.95)
    
    return best_category, confidence


def classify_complaint(text: str) -> dict:
    """
    Classify a complaint and return structured result.
    
    Args:
        text: The complaint text
        
    Returns:
        Dictionary with category, department, and confidence
    """
    category, confidence = keyword_based_classifier(text)
    department = CATEGORY_TO_DEPARTMENT.get(category, "Administrative Services")
    
    return {
        "category": category,
        "department": department,
        "confidence": round(confidence, 2)
    }
