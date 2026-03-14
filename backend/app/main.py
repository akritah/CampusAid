"""
CampusAid FastAPI application entrypoint.
"""

import logging
import os
from typing import Optional

from fastapi import FastAPI, Depends, File, Request, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.auth import get_current_user
from app.database import SessionLocal, get_db, get_database_info, init_db
from app.ml.complaint_classifier import ComplaintClassifier
from app.ml.multilingual_embedder import MultilingualEmbedder
from app.ml.speech_to_text import SpeechToText
from app.models import Complaint, ComplaintStatus, User, UserRole
from app.schemas import ComplaintCreateRequest, ComplaintSubmitResponse
from app.routes.admin_router import router as admin_router
from app.routes.auth_router import router as auth_router
from app.routes.complaints_router import router as complaints_router
from app.routes.complaints_router import submit_text_complaint, submit_voice_complaint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="CampusAid - Complaint Management System with Database",
    description="Multilingual complaint classification system with persistent storage",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_demo_users() -> None:
    demo_users = [
        {"username": "student1", "password": "student123", "role": UserRole.STUDENT},
        {"username": "worker1", "password": "worker123", "role": UserRole.WORKER},
        {"username": "admin1", "password": "admin123", "role": UserRole.ADMIN},
        {"username": "warden1", "password": "warden123", "role": UserRole.WARDEN},
    ]

    db = SessionLocal()
    created_users: list[str] = []

    try:
        for demo_user in demo_users:
            existing = db.query(User).filter(User.username == demo_user["username"]).first()
            if existing:
                continue

            db.add(
                User(
                    username=demo_user["username"],
                    hashed_password=get_password_hash(demo_user["password"]),
                    role=demo_user["role"],
                )
            )
            created_users.append(demo_user["username"])

        if created_users:
            db.commit()
            print(f"✅ Demo users created: {', '.join(created_users)}")
        else:
            print("ℹ️ Demo users already exist, skipping seeding")
    except Exception as exc:
        db.rollback()
        print(f"⚠️ Demo user seeding failed: {exc}")
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 70)
    print("🚀 STARTING CAMPUSAID SERVER")
    print("=" * 70)

    print("\n📊 Initializing database...")
    init_db()

    print("👤 Seeding demo users...")
    seed_demo_users()

    db_info = get_database_info()
    print(f"   Database Type: {db_info['type']}")
    print(f"   Database Location: {db_info['url']}")

    print("\n🚀 Loading ML models...")
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(backend_dir, "models", "complaint_classifier.pkl")

    embedder = MultilingualEmbedder()
    classifier = ComplaintClassifier(embedder=embedder)

    if os.path.exists(model_path):
        classifier.load(model_path)
        print("✅ Classifier loaded successfully")
    else:
        print("⚠️ Warning: Trained model not found!")
        print("   Please run: python backend/train_classifier.py")
        print("   Server will start but predictions will fail.")

    try:
        speech_to_text = SpeechToText(use_api=False)
        print("✅ Speech-to-text ready")
    except Exception as exc:
        speech_to_text = None
        print(f"⚠️ Speech-to-text not available: {exc}")

    app.state.embedder = embedder
    app.state.classifier = classifier
    app.state.speech_to_text = speech_to_text

    print("\n" + "=" * 70)
    print("✅ SERVER READY!")
    print("=" * 70 + "\n")


@app.get("/", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    db_info = get_database_info()

    try:
        total_complaints = db.query(Complaint).count()
        db_status = "connected"
    except Exception as exc:
        total_complaints = 0
        db_status = f"error: {str(exc)}"

    classifier_loaded = (
        hasattr(app.state, "classifier") and app.state.classifier.classifier is not None
    )
    speech_ready = hasattr(app.state, "speech_to_text") and app.state.speech_to_text is not None

    return {
        "status": "healthy",
        "service": "CampusAid - Multilingual Complaint System with Database",
        "version": "3.0.0",
        "features": {
            "text_complaints": True,
            "voice_complaints": speech_ready,
            "languages": ["Hindi", "English", "Hinglish"],
            "classifier_loaded": classifier_loaded,
            "database": db_status,
            "database_type": db_info["type"],
        },
        "statistics": {
            "total_complaints": total_complaints,
        },
    }


@app.get("/health", tags=["Health"])
async def service_health():
    return {"status": "running"}


@app.get("/stats", tags=["Admin"])
async def get_stats(
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

    total_complaints = base_query.with_entities(func.count(Complaint.id)).scalar() or 0

    resolved_complaints = (
        base_query.filter(Complaint.status == ComplaintStatus.RESOLVED)
        .with_entities(func.count(Complaint.id))
        .scalar()
        or 0
    )
    pending_complaints = max(total_complaints - resolved_complaints, 0)

    dept_total_rows = (
        base_query.with_entities(
            Complaint.department,
            func.count(Complaint.id).label("total"),
        )
        .group_by(Complaint.department)
        .all()
    )

    dept_resolved_rows = (
        base_query.filter(Complaint.status == ComplaintStatus.RESOLVED)
        .with_entities(
            Complaint.department,
            func.count(Complaint.id).label("resolved"),
        )
        .group_by(Complaint.department)
        .all()
    )

    dialect_name = db.bind.dialect.name if db.bind is not None else "postgresql"
    if dialect_name == "sqlite":
        resolution_days_expr = func.julianday(Complaint.resolved_at) - func.julianday(Complaint.created_at)
    else:
        resolution_days_expr = (
            (func.extract("epoch", Complaint.resolved_at) - func.extract("epoch", Complaint.created_at))
            / 86400.0
        )

    dept_avg_rows = (
        base_query.filter(Complaint.resolved_at.isnot(None), Complaint.created_at.isnot(None))
        .with_entities(
            Complaint.department,
            func.avg(resolution_days_expr).label("avg_days"),
        )
        .group_by(Complaint.department)
        .all()
    )

    resolved_by_department = {
        (department or "Unassigned"): int(count or 0)
        for department, count in dept_resolved_rows
    }
    avg_days_by_department = {
        (department or "Unassigned"): (float(avg_days) if avg_days is not None else None)
        for department, avg_days in dept_avg_rows
    }

    departments = []
    for department, total in dept_total_rows:
        name = department or "Unassigned"
        total_count = int(total or 0)
        resolved_count = resolved_by_department.get(name, 0)
        pending_count = max(total_count - resolved_count, 0)
        departments.append(
            {
                "name": name,
                "total": total_count,
                "resolved": resolved_count,
                "pending": pending_count,
                "avg_resolution_time_days": avg_days_by_department.get(name),
            }
        )

    departments.sort(key=lambda item: item["name"])

    return {
        "total_complaints": int(total_complaints),
        "resolved": int(resolved_complaints),
        "pending": int(pending_complaints),
        "departments": departments,
    }


@app.post("/submit-complaint", response_model=ComplaintSubmitResponse, tags=["Complaints"])
async def submit_complaint_alias(
    payload: ComplaintCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return await submit_text_complaint(payload=payload, request=request, db=db)


@app.post("/voice-complaint", response_model=ComplaintSubmitResponse, tags=["Complaints"])
async def submit_voice_complaint_alias(
    request: Request,
    audio_file: UploadFile = File(...),
    student_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return await submit_voice_complaint(
        request=request,
        audio_file=audio_file,
        student_id=student_id,
        db=db,
    )


app.include_router(complaints_router)
app.include_router(admin_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("STARTING CAMPUSAID BACKEND SERVER")
    print("=" * 70)
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
