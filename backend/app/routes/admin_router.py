from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Complaint, User, UserRole


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {UserRole.ADMIN, UserRole.WARDEN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or warden role required",
        )

    base_query = db.query(Complaint)
    if current_user.role == UserRole.WARDEN:
        base_query = base_query.filter(Complaint.department == "Hostel")

    total = base_query.with_entities(func.count(Complaint.id)).scalar()

    by_category = base_query.with_entities(
        Complaint.predicted_category,
        func.count(Complaint.id),
    ).group_by(Complaint.predicted_category).all()

    by_status = base_query.with_entities(
        Complaint.status,
        func.count(Complaint.id),
    ).group_by(Complaint.status).all()

    avg_confidence = base_query.with_entities(func.avg(Complaint.confidence_score)).scalar()

    return {
        "total_complaints": total,
        "by_category": {cat: count for cat, count in by_category},
        "by_status": {status.value: count for status, count in by_status},
        "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
        "scope": "hostel" if current_user.role == UserRole.WARDEN else "all_departments",
    }
