from typing import Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Complaint, ComplaintStatus, InputType, User, UserRole
from app.schemas import (
    ComplaintCreateRequest,
    ComplaintListResponse,
    ComplaintReadResponse,
    ComplaintStatusUpdateRequest,
    ComplaintSubmitResponse,
    ComplaintUpdateResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("", response_model=ComplaintSubmitResponse)
async def submit_text_complaint(
    payload: ComplaintCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    logger.info(f"Text complaint submission received (length: {len(payload.complaint_text)} chars)")
    
    try:
        classifier = request.app.state.classifier
        if classifier.classifier is None:
            logger.error("Classifier not loaded")
            raise HTTPException(
                status_code=503,
                detail="Classifier not loaded. Please train the model first.",
            )

        result = classifier.predict(payload.complaint_text)
        logger.info(f"Complaint classified: {result['predicted_category']} (confidence: {result['confidence_score']:.2f})")
        
        status = (
            ComplaintStatus.MANUAL_REVIEW
            if result["needs_review"]
            else ComplaintStatus.AUTO_ROUTED
        )

        db_complaint = Complaint(
            complaint_text=payload.complaint_text,
            input_type=InputType.TEXT,
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            status=status,
            department=result["predicted_category"],
            student_id=payload.student_id,
            contact=payload.contact,
        )

        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)

        logger.info(f"Complaint stored successfully (ID: {db_complaint.id}, Status: {status})")

        return ComplaintSubmitResponse(
            success=True,
            complaint_id=db_complaint.id,
            complaint_text=payload.complaint_text,
            department=db_complaint.department,
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            needs_manual_review=result["needs_review"],
            status=status,
            message=(
                f"Complaint stored successfully (ID: {db_complaint.id})"
                if not result["needs_review"]
                else f"Low confidence - marked for manual review (ID: {db_complaint.id})"
            ),
            all_probabilities=result["all_probabilities"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing complaint: {str(exc)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing complaint: {str(exc)}")


@router.post("/voice", response_model=ComplaintSubmitResponse)
async def submit_voice_complaint(
    request: Request,
    audio_file: UploadFile = File(...),
    student_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        speech_to_text = request.app.state.speech_to_text
        if speech_to_text is None:
            raise HTTPException(
                status_code=503,
                detail="Speech-to-text not available. Install: pip install openai-whisper",
            )

        classifier = request.app.state.classifier
        if classifier.classifier is None:
            raise HTTPException(
                status_code=503,
                detail="Classifier not loaded. Please train the model first.",
            )

        audio_bytes = await audio_file.read()
        transcription = speech_to_text.transcribe_from_bytes(
            audio_bytes,
            filename=audio_file.filename,
        )
        complaint_text = transcription["text"]

        if not complaint_text or len(complaint_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please try again with clearer audio.",
            )

        result = classifier.predict(complaint_text)
        status = (
            ComplaintStatus.MANUAL_REVIEW
            if result["needs_review"]
            else ComplaintStatus.AUTO_ROUTED
        )

        db_complaint = Complaint(
            complaint_text=complaint_text,
            input_type=InputType.VOICE,
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            status=status,
            department=result["predicted_category"],
            student_id=student_id,
            contact=None,
        )

        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)

        return ComplaintSubmitResponse(
            success=True,
            complaint_id=db_complaint.id,
            complaint_text=complaint_text,
            department=db_complaint.department,
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            needs_manual_review=result["needs_review"],
            status=status,
            message=f"Voice transcribed and stored (ID: {db_complaint.id}, Language: {transcription['language']})",
            all_probabilities=result["all_probabilities"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(exc)}")


@router.get("/{complaint_id}", response_model=ComplaintReadResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint #{complaint_id} not found")
    return complaint.to_dict()


@router.patch("/{id}", response_model=ComplaintUpdateResponse)
async def update_complaint_status(
    payload: ComplaintStatusUpdateRequest,
    id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if current_user.role not in {UserRole.ADMIN, UserRole.WARDEN}:
            raise HTTPException(status_code=403, detail="Admin or warden role required")

        complaint = db.query(Complaint).filter(Complaint.id == id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint #{id} not found")

        if current_user.role == UserRole.WARDEN and complaint.department != "Hostel":
            raise HTTPException(status_code=403, detail="Wardens can update only Hostel complaints")

        previous_status = complaint.status

        if payload.status is not None:
            complaint.status = payload.status

        if payload.notes is not None:
            complaint.notes = payload.notes

        if (
            payload.status is not None
            and payload.status == ComplaintStatus.RESOLVED
            and previous_status != ComplaintStatus.RESOLVED
        ):
            complaint.resolved_at = datetime.now(timezone.utc)

        complaint.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(complaint)

        return {
            "success": True,
            "message": f"Complaint #{id} updated",
            "complaint": complaint.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating complaint: {str(exc)}")


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    status: Optional[ComplaintStatus] = None,
    predicted_category: Optional[str] = None,
    department: Optional[str] = None,
    student_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ComplaintListResponse:
    query = db.query(Complaint)

    if status:
        query = query.filter(Complaint.status == status)

    if predicted_category:
        query = query.filter(Complaint.predicted_category == predicted_category)

    if department:
        query = query.filter(Complaint.department == department)

    if student_id:
        query = query.filter(Complaint.student_id == student_id)

    query = query.order_by(Complaint.created_at.desc())
    complaints = query.offset(offset).limit(limit).all()

    return {
        "total": len(complaints),
        "limit": limit,
        "offset": offset,
        "complaints": [complaint.to_dict() for complaint in complaints],
    }


@router.get("/meta/categories")
async def get_categories(request: Request):
    classifier = request.app.state.classifier
    if classifier.classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not loaded")

    return {
        "categories": classifier.categories,
        "total": len(classifier.categories),
    }
