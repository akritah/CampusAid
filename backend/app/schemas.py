"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models import ComplaintStatus, InputType, UserRole


class ComplaintCreateRequest(BaseModel):
    complaint_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Original complaint text submitted by user",
    )
    student_id: Optional[str] = Field(default=None, max_length=64)
    contact: Optional[str] = Field(default=None, max_length=255)

    @field_validator("complaint_text")
    @classmethod
    def normalize_complaint_text(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("complaint_text must be at least 10 characters long")
        return cleaned


class ComplaintStatusUpdateRequest(BaseModel):
    status: Optional[ComplaintStatus] = Field(default=None, description="New complaint status")
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None

    @model_validator(mode="after")
    def validate_any_field_present(self):
        if self.status is None and self.notes is None:
            raise ValueError("At least one of status or notes must be provided")
        return self


class ComplaintSubmitResponse(BaseModel):
    success: bool
    complaint_id: int
    complaint_text: str
    department: Optional[str] = None
    predicted_category: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    status: ComplaintStatus
    needs_manual_review: bool
    message: str
    all_probabilities: Optional[dict[str, float]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "complaint_id": 123,
                "complaint_text": "Hot water not available in hostel",
                "department": "Hostel",
                "predicted_category": "Hostel",
                "confidence_score": 0.87,
                "status": "auto_routed",
                "needs_manual_review": False,
                "message": "Complaint stored successfully (ID: 123)",
                "all_probabilities": {
                    "Hostel": 0.87,
                    "IT": 0.06,
                    "Academic": 0.03,
                },
            }
        }
    )


class ComplaintReadResponse(BaseModel):
    id: int
    complaint_text: str
    input_type: InputType
    predicted_category: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    status: ComplaintStatus
    department: Optional[str] = None
    student_id: Optional[str] = None
    contact: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None


class ComplaintListResponse(BaseModel):
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=200)
    offset: int = Field(..., ge=0)
    complaints: list[ComplaintReadResponse]


class ComplaintUpdateResponse(BaseModel):
    success: bool
    message: str
    complaint: ComplaintReadResponse


class AuthRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole


class AuthLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole


class AuthRegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    username: str
    role: UserRole


class AuthLoginResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    username: str
    role: UserRole
