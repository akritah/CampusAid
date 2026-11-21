"""
DATABASE CONNECTION MODULE
==========================
Purpose: Centralized PostgreSQL configuration and session management

POSTGRESQL CONNECTION
---------------------
This project uses SQLAlchemy ORM with PostgreSQL.
Connection is read from the DATABASE_URL environment variable.

Expected format:
    postgresql+psycopg2://username:password@host:5432/campusaid

Example:
    DATABASE_URL=postgresql+psycopg2://postgres:password@host:5432/campusaid

If DATABASE_URL is not set, local development uses the repository SQLite database.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'campusaid.db')}"

# Database URL (PostgreSQL)
# Reads from environment variable for deployment flexibility.
# Format: postgresql+psycopg2://username:password@host:5432/campusaid
APP_ENV = os.getenv("APP_ENV", "development").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip() or DEFAULT_SQLITE_URL
if DATABASE_URL.startswith("postgres://"):
    # Render's dashboard may provide the legacy scheme; SQLAlchemy 2 expects
    # postgresql:// (which selects the installed psycopg2 driver).
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
if APP_ENV == "production" and DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("Production requires DATABASE_URL to point to a persistent PostgreSQL database")

engine_kwargs = {"echo": os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes", "on"}}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({"pool_pre_ping": True, "pool_size": 5, "max_overflow": 5})

# Create PostgreSQL engine
# Engine manages DB connections and pooling for SQLAlchemy sessions.
# echo=False keeps SQL logs clean; set True when debugging queries.
engine = create_engine(DATABASE_URL, **engine_kwargs)

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

        # Lightweight migration for legacy SQLite databases created before
        # priority/root_cause fields were introduced.
        if DATABASE_URL.startswith("sqlite"):
            with engine.begin() as conn:
                table_info = conn.execute(text("PRAGMA table_info(complaints)")).fetchall()
                existing_columns = {row[1] for row in table_info}

                if "priority" not in existing_columns:
                    conn.execute(
                        text("ALTER TABLE complaints ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'")
                    )

                if "root_cause" not in existing_columns:
                    conn.execute(
                        text("ALTER TABLE complaints ADD COLUMN root_cause VARCHAR(50) DEFAULT 'unknown'")
                    )

                if "owner_id" not in existing_columns:
                    conn.execute(text("ALTER TABLE complaints ADD COLUMN owner_id INTEGER"))

        if "postgresql" in DATABASE_URL:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS owner_id INTEGER"))

        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_complaints_owner_id ON complaints (owner_id)"))

        # Normalize priority values for existing records. Harassment should
        # never remain medium/low by default.
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE complaints
                    SET priority = CASE
                        WHEN lower(predicted_category) = 'harassment' THEN 'critical'
                        WHEN lower(predicted_category) IN ('infrastructure', 'it') THEN 'high'
                        WHEN lower(predicted_category) IN ('hostel', 'academic', 'administration') THEN 'medium'
                        ELSE COALESCE(priority, 'medium')
                    END
                    WHERE priority IS NULL
                       OR lower(priority) NOT IN ('low', 'medium', 'high', 'critical')
                       OR (lower(predicted_category) = 'harassment' AND lower(COALESCE(priority, 'medium')) IN ('low', 'medium'))
                    """
                )
            )

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
