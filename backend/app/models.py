"""
DATABASE MODELS
===============
Purpose: Define database table structures using SQLAlchemy ORM

WHY ORM (Object-Relational Mapping)?
-------------------------------------
Instead of writing SQL:
    CREATE TABLE complaints (id INTEGER PRIMARY KEY, text TEXT, ...);
    INSERT INTO complaints VALUES (1, 'Hot water issue', ...);

We write Python:
    complaint = Complaint(text='Hot water issue', ...)
    db.add(complaint)
    db.commit()

Benefits:
- Type safety (Python checks types)
- Database agnostic (works with SQLite, PostgreSQL, MySQL)
- Easier to maintain
- Less SQL injection risk
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, CheckConstraint
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


# ============================================================================
# ENUMS (Predefined choices)
# ============================================================================

class InputType(str, enum.Enum):
    """
    How the complaint was submitted.
    
    TEXT: User typed the complaint
    VOICE: User uploaded audio file
    """
    TEXT = "text"
    VOICE = "voice"


class ComplaintStatus(str, enum.Enum):
    """
    Current status of the complaint.
    
    AUTO_ROUTED: High confidence, automatically sent to department
    MANUAL_REVIEW: Low confidence, needs human verification
    IN_PROGRESS: Department is working on it
    RESOLVED: Complaint has been resolved
    CLOSED: Complaint closed (resolved or rejected)
    """
    AUTO_ROUTED = "auto_routed"
    MANUAL_REVIEW = "manual_review"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class UserRole(str, enum.Enum):
    STUDENT = "student"
    WORKER = "worker"
    ADMIN = "admin"
    WARDEN = "warden"


# ============================================================================
# COMPLAINT MODEL (Database Table)
# ============================================================================

class Complaint(Base):
    """
    Complaint table - stores all submitted complaints.
    
    WHY STORE COMPLAINTS IN DATABASE?
    ----------------------------------
    Before: Complaints via email/phone → Lost, no tracking, no analytics
    After: All complaints in one place → Track, analyze, improve
    
    WHAT GETS STORED?
    -----------------
    1. Original complaint text (what user said)
    2. How it was submitted (text/voice)
    3. ML prediction (category + confidence)
    4. Status (auto-routed or needs review)
    5. Department assigned
    6. Timestamps (when created, updated)
    
    WHY FRONTEND DOESN'T ACCESS DATABASE DIRECTLY?
    -----------------------------------------------
    Security: Frontend is in browser (anyone can inspect)
    Control: Backend validates, sanitizes, and controls access
    ML Integration: Backend runs ML before storing
    Business Logic: Backend enforces rules (e.g., confidence threshold)
    """
    
    # Table name in database
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name="ck_complaints_confidence_range"),
        CheckConstraint("length(trim(complaint_text)) >= 10", name="ck_complaints_text_min_length"),
    )
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Unique complaint ID (auto-generated)"
    )
    # Why auto-increment? Database generates unique IDs automatically
    
    # ========================================================================
    # COMPLAINT CONTENT
    # ========================================================================
    
    complaint_text = Column(
        String(5000),
        nullable=False,
        comment="Original complaint text (in any language)"
    )
    # Why String? Can store text of any length
    # Why nullable=False? Every complaint must have text
    
    input_type = Column(
        SQLEnum(InputType),
        nullable=False,
        default=InputType.TEXT,
        comment="How complaint was submitted (text/voice)"
    )
    # Why Enum? Only allow specific values (text or voice)
    # Why default=TEXT? Most complaints are text
    
    # ========================================================================
    # ML PREDICTION RESULTS
    # ========================================================================
    
    predicted_category = Column(
        String(100),
        nullable=False,
        index=True,
        comment="ML predicted category (Hostel, IT, Academic, etc.)"
    )
    # Why index=True? Fast searching by category
    # Example: "Find all Hostel complaints"
    
    confidence_score = Column(
        Float,
        nullable=False,
        comment="ML confidence (0.0 to 1.0, e.g., 0.87 = 87%)"
    )
    # Why Float? Decimal numbers (0.87, 0.92, etc.)
    # Why store confidence? Track ML accuracy, identify uncertain cases
    
    # ========================================================================
    # COMPLAINT STATUS & ROUTING
    # ========================================================================
    
    status = Column(
        SQLEnum(ComplaintStatus),
        nullable=False,
        default=ComplaintStatus.AUTO_ROUTED,
        index=True,
        comment="Current status (auto_routed, manual_review, etc.)"
    )
    # Why index=True? Fast filtering by status
    # Example: "Show all complaints needing manual review"
    
    department = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Department assigned to handle complaint"
    )
    # Why nullable=True? May not be assigned immediately
    # Why index=True? Fast filtering by department
    
    # ========================================================================
    # STUDENT INFORMATION (Optional)
    # ========================================================================
    
    student_id = Column(
        String,
        nullable=True,
        index=True,
        comment="Student ID (optional, for tracking)"
    )
    # Why optional? Anonymous complaints allowed
    # Why index=True? Fast lookup of student's complaints
    
    contact = Column(
        String,
        nullable=True,
        comment="Contact email/phone (optional)"
    )
    # Why optional? Anonymous complaints allowed
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When complaint was submitted"
    )
    # Why server_default=func.now()? Database sets timestamp automatically
    # Why timezone=True? Store timezone info (important for global systems)
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When complaint was last updated"
    )
    # Why onupdate=func.now()? Auto-update timestamp on any change
    
    # ========================================================================
    # ADDITIONAL METADATA
    # ========================================================================
    
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When complaint was resolved (if resolved)"
    )
    # Why nullable=True? Only set when resolved
    
    notes = Column(
        String,
        nullable=True,
        comment="Admin notes (internal use)"
    )
    # Why nullable=True? Not all complaints need notes
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self):
        """
        String representation for debugging.
        
        Example: <Complaint #123: Hostel (87%)>
        """
        return f"<Complaint #{self.id}: {self.predicted_category} ({self.confidence_score:.0%})>"
    
    def to_dict(self):
        """
        Convert complaint to dictionary (for JSON responses).
        
        Returns:
            dict with all complaint fields
        """
        return {
            "id": self.id,
            "complaint_text": self.complaint_text,
            "input_type": self.input_type.value if self.input_type else None,
            "predicted_category": self.predicted_category,
            "confidence_score": self.confidence_score,
            "status": self.status.value if self.status else None,
            "department": self.department,
            "student_id": self.student_id,
            "contact": self.contact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "notes": self.notes
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User #{self.id}: {self.username} ({self.role.value})>"


# ============================================================================
# EXAMPLE USAGE (for understanding)
# ============================================================================

if __name__ == "__main__":
    """
    This shows how to use the Complaint model.
    Run: python -m app.models
    """
    print("=" * 70)
    print("COMPLAINT MODEL STRUCTURE")
    print("=" * 70)
    
    # Show all columns
    print("\nTable Name:", Complaint.__tablename__)
    print("\nColumns:")
    for column in Complaint.__table__.columns:
        print(f"  - {column.name}: {column.type} (nullable={column.nullable})")
    
    print("\n" + "=" * 70)
    print("MODEL DEFINED SUCCESSFULLY!")
    print("=" * 70)
