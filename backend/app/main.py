"""
CampusAid FastAPI application entrypoint.
"""

import logging
import os
import json
from typing import Optional

from fastapi import FastAPI, Depends, File, Form, Request, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.auth import get_password_hash, get_current_user, validate_auth_settings
from app.database import SessionLocal, get_db, get_database_info, init_db
from app.models import Complaint, ComplaintStatus, User, UserRole
from app.schemas import ComplaintCreateRequest, ComplaintSubmitResponse
from app.routes.admin_router import router as admin_router
from app.routes.auth_router import router as auth_router
from app.routes.complaints_router import router as complaints_router
from app.routes.complaints_router import submit_text_complaint, transcribe_voice_complaint
from app.routes.policy_router import router as policy_router

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
    docs_url="/docs" if os.getenv("APP_ENV", "development").lower() != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if os.getenv("APP_ENV", "development").lower() != "production" else None,
)

cors_origins = [origin.strip().rstrip("/") for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
if os.getenv("APP_ENV", "development").lower() == "production" and not cors_origins:
    raise RuntimeError("CORS_ORIGINS must include the deployed frontend origin in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_demo_users() -> None:
    raw_users = os.getenv("DEMO_USERS_JSON", "").strip()
    if not raw_users:
        logger.info("DEMO_USERS_JSON is unset; skipping demo account seeding")
        return

    try:
        configured_users = json.loads(raw_users)
        if not isinstance(configured_users, list):
            raise ValueError("DEMO_USERS_JSON must be a JSON array")
        demo_users = [
            {
                "username": str(item["username"]).strip(),
                "password": str(item["password"]),
                "role": UserRole(str(item["role"]).lower()),
            }
            for item in configured_users
        ]
        if any(not item["username"] or len(item["password"]) < 12 for item in demo_users):
            raise ValueError("Demo usernames must be non-empty and passwords at least 12 characters")
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid DEMO_USERS_JSON configuration: {exc}") from exc

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
            logger.info("Configured demo accounts created: %s", ", ".join(created_users))
    except Exception as exc:
        db.rollback()
        print(f"⚠️ Demo user seeding failed: {exc}")
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    validate_auth_settings()
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
    # Import model libraries only after the API process starts; module import is
    # also used by migrations and lightweight API smoke tests.
    from app.ml.complaint_classifier import ComplaintClassifier
    from app.ml.multilingual_embedder import MultilingualEmbedder
    from app.ml.speech_to_text import SpeechToText

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.getenv("CLASSIFIER_MODEL_PATH", os.path.join(backend_dir, "models", "complaint_classifier.pkl"))

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
async def service_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    classifier_loaded = hasattr(app.state, "classifier") and app.state.classifier.classifier is not None
    if not classifier_loaded:
        raise HTTPException(status_code=503, detail="Complaint classifier unavailable")
    return {"status": "healthy", "database": "connected", "classifier": "ready"}


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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await submit_text_complaint(payload=payload, request=request, current_user=current_user, db=db)


@app.post("/voice-complaint", tags=["Complaints"])
async def submit_voice_complaint_alias(
    request: Request,
    current_user: User = Depends(get_current_user),
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(default=None),
):
    return await transcribe_voice_complaint(
        request=request,
        current_user=current_user,
        audio_file=audio_file,
        language=language,
    )


app.include_router(complaints_router)
app.include_router(admin_router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(policy_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
