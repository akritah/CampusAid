"""Isolated synchronous smoke checks for production auth, retrieval, and data scope."""
import atexit
import os
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
_test_home = tempfile.TemporaryDirectory(prefix=".smoke-test-", dir=str(BACKEND_DIR))
atexit.register(_test_home.cleanup)
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_home.name, "test.sqlite")).replace("\\", "/")
os.environ["POLICY_STORAGE_DIR"] = str(Path(_test_home.name, "policies"))
os.environ["SECRET_KEY"] = "smoke-test-secret-that-is-long-enough-to-sign-tokens"

from fastapi import HTTPException  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials  # noqa: E402
from app.auth import create_access_token, get_current_user  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Complaint, ComplaintStatus, InputType, User, UserRole  # noqa: E402
from app.policy_qa import POLICY_DIR, answer  # noqa: E402

atexit.register(engine.dispose)
Base.metadata.create_all(engine)


class ProductionSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.student = User(username="smoke_student", hashed_password="test-only", role=UserRole.STUDENT)
        cls.other_student = User(username="smoke_other", hashed_password="test-only", role=UserRole.STUDENT)
        cls.admin = User(username="smoke_admin", hashed_password="test-only", role=UserRole.ADMIN)
        cls.db.add_all([cls.student, cls.other_student, cls.admin])
        cls.db.commit()
        for user in (cls.student, cls.other_student, cls.admin):
            cls.db.refresh(user)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_bearer_token_authentication(self):
        token = create_access_token(self.student)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        self.assertEqual(get_current_user(credentials, self.db).id, self.student.id)
        with self.assertRaises(HTTPException):
            get_current_user(HTTPAuthorizationCredentials(scheme="Basic", credentials="not-accepted"), self.db)

    def test_policy_citation_and_abstention(self):
        POLICY_DIR.mkdir(parents=True, exist_ok=True)
        (POLICY_DIR / "attendance-policy.txt").write_text(
            "Students must attend at least 75 percent of scheduled classes to qualify for examinations.",
            encoding="utf-8",
        )
        grounded = answer("What attendance percentage qualifies students for examinations?")
        self.assertFalse(grounded["abstained"])
        self.assertEqual(grounded["sources"][0]["document"], "attendance-policy.txt")
        self.assertIn("75 percent", grounded["sources"][0]["quote"])
        unsupported = answer("What is the penalty for owning an electric scooter?")
        self.assertTrue(unsupported["abstained"])
        self.assertEqual(unsupported["sources"], [])

    def test_grievance_storage_and_student_scope(self):
        complaint = Complaint(
            complaint_text="Title: Test\n\nDescription: Hostel water supply is unavailable.",
            input_type=InputType.TEXT,
            predicted_category="Hostel",
            confidence_score=0.92,
            status=ComplaintStatus.AUTO_ROUTED,
            department="Hostel",
            student_id=str(self.student.id),
            owner_id=self.student.id,
        )
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)

        own = self.db.query(Complaint).filter(Complaint.owner_id == self.student.id).all()
        other = self.db.query(Complaint).filter(Complaint.owner_id == self.other_student.id).all()
        self.assertIn(complaint.id, [item.id for item in own])
        self.assertNotIn(complaint.id, [item.id for item in other])

    def test_deployment_routes_are_registered(self):
        routes = {(route.path, method) for route in app.routes for method in getattr(route, "methods", set())}
        for route in (
            ("/health", "GET"),
            ("/auth/login", "POST"),
            ("/submit-complaint", "POST"),
            ("/complaints", "GET"),
            ("/policy/ask", "POST"),
            ("/policy/documents", "POST"),
        ):
            self.assertIn(route, routes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
