"""Local policy document retrieval with extractive, citation-backed answers."""
from __future__ import annotations

import re
import os
import logging
import time
import requests
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from fastapi import HTTPException

POLICY_DIR = Path(os.getenv("POLICY_STORAGE_DIR", str(Path(__file__).resolve().parents[1] / "policy_documents"))).expanduser()
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)
logger = logging.getLogger(__name__)
STOP_WORDS = {"a", "an", "am", "and", "are", "as", "at", "be", "but", "by", "can", "campus", "could", "did", "do", "does", "for", "from", "had", "has", "have", "he", "her", "here", "how", "i", "in", "is", "it", "its", "me", "my", "of", "on", "or", "our", "please", "should", "that", "the", "their", "them", "there", "these", "they", "this", "those", "to", "under", "us", "was", "we", "were", "what", "when", "where", "which", "who", "will", "with", "would", "you", "your", "policy", "university"}


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


def _extract(path: Path) -> str:
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            # PyPDF2 keeps local installs working where pypdf is not available.
            from PyPDF2 import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    if path.suffix.lower() == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    return ""


def _chunks(source: str, text: str) -> list[Chunk]:
    # Paragraph-oriented passages retain section headings and stay quoteable.
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    result: list[Chunk] = []
    current = ""
    for paragraph in paragraphs:
        if not paragraph:
            continue
        if len(current) + len(paragraph) > 1100 and current:
            result.append(Chunk(source, current))
            current = ""
        current = f"{current}\n{paragraph}".strip()
    if current:
        result.append(Chunk(source, current))
    return result


def _normalize_term(term: str) -> str:
    """Normalize common inflections and equivalent grievance wording for retrieval."""
    term = term.lower()
    if term in {"file", "files", "filed", "filing", "submit", "submits", "submitted", "submitting"}:
        return "submit"
    if term in {"criteria", "criterion", "eligible", "eligibility"}:
        return "requirement"
    if term in {"exam", "exams", "examination", "examinations", "endterm", "endterms"}:
        return "exam"
    if term in {"sit", "appear", "appears", "appearing"}:
        return "appear"
    if term.endswith("ies") and len(term) > 4:
        return term[:-3] + "y"
    if term.endswith("s") and len(term) > 3:
        return term[:-1]
    return term


@lru_cache(maxsize=256)
def _cached_chunks(path_text: str, modified_ns: int, size: int) -> tuple[Chunk, ...]:
    """Cache extracted passages by file version; changed uploads get a new key."""
    path = Path(path_text)
    return tuple(_chunks(path.name, _extract(path)))


def retrieve(question: str, limit: int = 4) -> list[tuple[Chunk, float]]:
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    terms = {_normalize_term(t) for t in TOKEN_RE.findall(question)} - STOP_WORDS
    if not terms:
        return []
    scored: list[tuple[Chunk, float]] = []
    for path in sorted(POLICY_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.name.lower() == "readme.md":
            continue
        try:
            stat = path.stat()
            passages = _cached_chunks(str(path), stat.st_mtime_ns, stat.st_size)
        except Exception:
            continue
        for chunk in passages:
            words = [_normalize_term(t) for t in TOKEN_RE.findall(chunk.text)]
            word_set = set(words)
            overlap = terms & word_set
            if not overlap:
                continue
            # Require meaningful coverage; exact phrase matches are a small bonus.
            coverage = len(overlap) / len(terms)
            if len(terms) > 1 and len(overlap) < 2:
                continue
            density = len(overlap) / max(len(word_set), 1)
            score = coverage * 0.85 + min(density * 8, 0.15)
            scored.append((chunk, score))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:limit]


def answer(question: str) -> dict:
    matches = retrieve(question)
    # Require a useful absolute score and keep only passages close to the best
    # match, so a weak overlap elsewhere cannot dilute the answer.
    best_score = matches[0][1] if matches else 0
    relevance_floor = max(0.18, best_score * 0.75)
    grounded = [(chunk, score) for chunk, score in matches if score >= relevance_floor]
    sources = [
        {"document": chunk.source, "quote": chunk.text[:900], "relevance": round(score, 3)}
        for chunk, score in grounded
    ]
    generated = _gemini_answer(question, sources)
    if generated:
        return {
            "answer": generated,
            "abstained": False,
            "sources": sources,
            "answer_type": "policy" if sources else "general",
        }
    if not sources:
        raise HTTPException(
            status_code=503,
            detail="Gemini could not generate a response. Check the backend Gemini API key and network connection, then try again.",
        )
    return {
        "answer": "The matching policy text is shown in the cited sources below.",
        "abstained": False,
        "sources": sources,
        "answer_type": "policy",
    }


def _gemini_answer(question: str, sources: list[dict]) -> str | None:
    """Generate an answer using retrieved text, or general help when none matches."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        if sources:
            context = "\n\n".join(
                f'SOURCE: {source["document"]}\nPASSAGE: {source["quote"]}' for source in sources
            )
            instruction = (
                "Answer the student's question using only the source passages below. Be concise, "
                "and cite sources inline using [filename]. If the passages do not contain the answer, "
                "say the documents do not specify it and suggest contacting the relevant office. "
                "Do not invent rules or facts.\n\nRetrieved source passages:\n" + context
            )
        else:
            instruction = (
                "Give the student a useful, direct general answer in 3-5 sentences using common "
                "higher-education practice and practical next steps. This is not a university policy "
                "lookup: do not pretend the answer is Bennett University's rule and do not replace "
                "the answer with a generic disclaimer. If exact local requirements may vary, add one "
                "short final sentence saying to confirm the exact threshold with the academic office. "
                "For an attendance question about exam eligibility, explain that many universities "
                "set a minimum attendance threshold, students should check their course handbook or "
                "student portal, and anyone at risk should contact the instructor/advisor early about "
                "documented absences and any make-up or condonation process. Do not invent an exact "
                "percentage or claim an exception is guaranteed."
            )
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        result = None
        for attempt in range(3):
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/interactions",
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json={"model": model, "input": instruction + "\n\nStudent question: " + question},
                timeout=(5, 12),
            )
            if response.ok:
                result = response.json()
                break
            # Retry only transient rate limit/service errors; never wait long on a
            # bad key, invalid model, or malformed request.
            if response.status_code not in {429, 500, 502, 503, 504} or attempt == 2:
                logger.warning("Gemini API returned %s: %s", response.status_code, response.text[:300])
                response.raise_for_status()
            time.sleep(0.5 * (attempt + 1))

        if not result:
            return None
        if result.get("output_text"):
            return result["output_text"].strip()
        return "\n".join(
            part.get("text", "")
            for step in result.get("steps", [])
            if step.get("type") == "model_output"
            for part in step.get("content", [])
            if part.get("type") == "text" and part.get("text")
        ).strip() or None
    except Exception:
        logger.exception("Gemini answer request failed")
        return None
