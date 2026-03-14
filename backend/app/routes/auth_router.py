from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import authenticate_user, get_password_hash
from app.database import get_db
from app.models import User, UserRole
from app.schemas import AuthLoginRequest, AuthLoginResponse, AuthRegisterRequest, AuthRegisterResponse


router = APIRouter()


@router.post("/register", response_model=AuthRegisterResponse)
async def register_user(payload: AuthRegisterRequest, db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Registration attempt for username: {payload.username}")
    
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        logger.warning(f"Registration failed: Username {payload.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    if payload.role not in {UserRole.STUDENT, UserRole.WORKER, UserRole.ADMIN, UserRole.WARDEN}:
        logger.warning(f"Registration failed: Invalid role {payload.role}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Allowed: student, worker, admin, warden",
        )

    user = User(
        username=payload.username.strip(),
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User registered successfully: {user.username} (ID: {user.id}, Role: {user.role})")

    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    }


@router.post("/login", response_model=AuthLoginResponse)
async def login(payload: AuthLoginRequest, db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Login attempt for username: {payload.username}")
    
    user = authenticate_user(db, payload.username.strip(), payload.password)
    if user is None:
        logger.warning(f"Login failed: Invalid credentials for username {payload.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    logger.info(f"Login successful: {user.username} (ID: {user.id}, Role: {user.role})")

    return {
        "success": True,
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    }
