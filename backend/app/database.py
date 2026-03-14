"""
DATABASE CONNECTION MODULE
==========================
Purpose: Centralized PostgreSQL configuration and session management

POSTGRESQL CONNECTION
---------------------
This project uses SQLAlchemy ORM with PostgreSQL.
Connection is read from the DATABASE_URL environment variable.

Expected format:
    postgresql+psycopg2://username:password@localhost:5432/campusaid

Example:
    DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/campusaid

If DATABASE_URL is not set, a local PostgreSQL default is used.
"""

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database URL (PostgreSQL)
# Reads from environment variable for deployment flexibility.
# Format: postgresql+psycopg2://username:password@localhost:5432/campusaid
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/campusaid"
)

# Create PostgreSQL engine
# Engine manages DB connections and pooling for SQLAlchemy sessions.
# echo=False keeps SQL logs clean; set True when debugging queries.
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory bound to PostgreSQL engine
# Session = Database transaction manager
# autocommit=False: Manual commit (safer)
# autoflush=False: Manual flush (more control)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()


# ============================================================================
# DATABASE SESSION DEPENDENCY
# ============================================================================

def get_db():
    """
    Get database session for API endpoints.
    
    This is a FastAPI dependency that:
    1. Creates a new database session
    2. Yields it to the endpoint
    3. Closes it after the request (even if error occurs)
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    
    WHY THIS PATTERN?
    -----------------
    - Automatic session management (no manual close needed)
    - Each request gets its own session (thread-safe)
    - Sessions are always closed (no memory leaks)
    - Errors don't leave sessions open
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize database by creating all tables.
    
    This function:
    1. Imports all models (so SQLAlchemy knows about them)
    2. Creates tables if they don't exist
    3. Does nothing if tables already exist
    
    Call this when starting the application.
    """
    try:
        from app.models import Complaint, User  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except SQLAlchemyError as exc:
        message = (
            "❌ Database initialization failed. "
            "Verify DATABASE_URL and ensure PostgreSQL is running. "
            f"Details: {exc}"
        )
        print(message)
        raise RuntimeError(message) from exc


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_database_info():
    """
    Get information about the database.
    
    Returns:
        dict with database type, location, and status
    """
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "Other"

    return {
        "type": db_type,
        "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
        "status": "connected"
    }


# ============================================================================
# EXAMPLE USAGE (for understanding)
# ============================================================================

if __name__ == "__main__":
    """
    This shows how to use the database module.
    Run: python -m app.database
    """
    print("=" * 70)
    print("DATABASE MODULE TEST")
    print("=" * 70)
    
    # Initialize database
    init_db()
    
    # Get database info
    info = get_database_info()
    print(f"\nDatabase Type: {info['type']}")
    print(f"Database Location: {info['url']}")
    print(f"Status: {info['status']}")
    
    # Test session creation
    db = SessionLocal()
    print("\n✅ Database session created successfully")
    db.close()
    print("✅ Database session closed successfully")
    
    print("\n" + "=" * 70)
    print("DATABASE MODULE WORKING CORRECTLY!")
    print("=" * 70)
