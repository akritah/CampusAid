"""
Category to Department mapping for complaint management system.
Maps complaint categories to their responsible departments.
"""

CATEGORY_TO_DEPARTMENT = {
    "IT": "Information Technology",
    "Infrastructure": "Facilities & Infrastructure",
    "Hostel": "Hostel Management",
    "Academic": "Academic Affairs",
    "Harassment": "Human Resources",
    "Administration": "Administrative Services",
}

# Reverse mapping for lookups
DEPARTMENT_TO_CATEGORY = {v: k for k, v in CATEGORY_TO_DEPARTMENT.items()}

# Valid categories
VALID_CATEGORIES = list(CATEGORY_TO_DEPARTMENT.keys())

# Valid departments
VALID_DEPARTMENTS = list(CATEGORY_TO_DEPARTMENT.values())


def get_department_for_category(category: str) -> str:
    """
    Get the department responsible for a given complaint category.
    
    Args:
        category: The complaint category
        
    Returns:
        The department name, or None if category is not found
    """
    return CATEGORY_TO_DEPARTMENT.get(category)


def get_category_for_department(department: str) -> str:
    """
    Get the complaint category for a given department.
    
    Args:
        department: The department name
        
    Returns:
        The category, or None if department is not found
    """
    return DEPARTMENT_TO_CATEGORY.get(department)


def is_valid_category(category: str) -> bool:
    """
    Check if a category is valid.
    
    Args:
        category: The category to validate
        
    Returns:
        True if valid, False otherwise
    """
    return category in VALID_CATEGORIES


def is_valid_department(department: str) -> bool:
    """
    Check if a department is valid.
    
    Args:
        department: The department to validate
        
    Returns:
        True if valid, False otherwise
    """
    return department in VALID_DEPARTMENTS
