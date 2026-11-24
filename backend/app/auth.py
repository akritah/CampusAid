from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
import secrets

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)
_development_secret = secrets.token_urlsafe(48)


def _secret_key() -> str:
    secret = os.getenv("SECRET_KEY", "").strip()
    if not secret:
        if os.getenv("APP_ENV", "development").lower() == "production":
            raise RuntimeError("SECRET_KEY must be set in production")
        return _development_secret
    if len(secret) < 32 and os.getenv("APP_ENV", "development").lower() == "production":
        raise RuntimeError("SECRET_KEY must contain at least 32 characters in production")
    return secret


def validate_auth_settings() -> None:
    """Fail during startup when production token signing is misconfigured."""
    _secret_key()


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user.id), "role": user.role.value, "iat": now, "exp": now + timedelta(hours=12)},
        _secret_key(),
        algorithm="HS256",
    )

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid bearer token required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, _secret_key(), algorithms=["HS256"])
        user_id = int(payload.get("sub", ""))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise unauthorized
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
