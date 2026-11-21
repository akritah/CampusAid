"""Priority mapping helpers for complaint categories."""

from app.models import Priority


DEFAULT_PRIORITY_BY_CATEGORY: dict[str, Priority] = {
    "harassment": Priority.CRITICAL,
    "infrastructure": Priority.HIGH,
    "it": Priority.HIGH,
    "hostel": Priority.MEDIUM,
    "academic": Priority.MEDIUM,
    "administration": Priority.MEDIUM,
}


def get_priority_for_category(category: str | None) -> Priority:
    """Return default priority for a predicted category."""
    if not category:
        return Priority.MEDIUM

    return DEFAULT_PRIORITY_BY_CATEGORY.get(category.strip().lower(), Priority.MEDIUM)
