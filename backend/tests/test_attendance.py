from datetime import datetime, timezone

import numpy as np

from app.cv.matcher import serialize_embedding
from app.database import SessionLocal
from app.models import Role, Student, User
from app.services import record_attendance


def test_duplicate_attendance_is_prevented():
    with SessionLocal() as db:
        guard = User(username="guard", password_hash="not-used", role=Role.SECURITY)
        student = Student(student_id="S1", name="Ada", department="CSE", year=4, photo_path="x.jpg", face_embedding=serialize_embedding(np.ones(4)))
        db.add_all([guard, student]); db.commit()
        _, first = record_attendance(db, student, guard, 0.8)
        _, second = record_attendance(db, student, guard, 0.8)
        assert first is True
        assert second is False
