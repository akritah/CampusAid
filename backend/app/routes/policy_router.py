from pathlib import Path
import re
import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.models import User, UserRole
from app.policy_qa import POLICY_DIR, SUPPORTED_EXTENSIONS, answer

router = APIRouter(prefix="/policy", tags=["University Policy Q&A"])


class PolicyQuestion(BaseModel):
    question: str = Field(min_length=5, max_length=1000)


@router.post("/ask")
async def ask_policy_question(
    payload: PolicyQuestion,
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.STUDENT, UserRole.WORKER}:
        raise HTTPException(status_code=403, detail="Student portal access required")
    # Policy document extraction is synchronous filesystem/PDF work; move it off
    # the event loop so concurrent API requests stay responsive.
    return await asyncio.to_thread(answer, payload.question)


@router.post("/documents", status_code=201)
async def upload_policy_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {UserRole.ADMIN, UserRole.WARDEN}:
        raise HTTPException(status_code=403, detail="Admin or warden role required")
    name = Path(file.filename or "").name
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Upload a TXT, Markdown, PDF, or DOCX policy document")
    content = await file.read(15 * 1024 * 1024 + 1)
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Policy document must be 15 MB or smaller")
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded document is empty")
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or f"policy{suffix}"
    destination = POLICY_DIR / safe_name
    temporary = destination.with_suffix(destination.suffix + ".uploading")
    temporary.write_bytes(content)
    temporary.replace(destination)
    return {"document": safe_name, "message": "Policy document added to the searchable library"}
