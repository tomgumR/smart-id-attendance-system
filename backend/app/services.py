from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Attendance, Student, User, VerificationMode


def attendance_to_dict(row: Attendance) -> dict:
    return {
        "id": row.id, "student_id": row.student.student_id, "name": row.student.name,
        "department": row.student.department, "timestamp": row.timestamp,
        "verification_mode": row.verification_mode, "similarity_score": row.similarity_score,
        "security_username": row.security_user.username,
    }


def record_attendance(db: Session, student: Student, guard: User, score: float) -> tuple[Attendance, bool]:
    now = datetime.now(timezone.utc)
    day = now.date().isoformat()
    existing = db.scalar(select(Attendance).where(Attendance.student_id == student.id, Attendance.attendance_date == day))
    if existing:
        return existing, False
    row = Attendance(student_id=student.id, attendance_date=day, timestamp=now, verification_mode=VerificationMode.ID_ONLY, similarity_score=score, security_user_id=guard.id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(Attendance).where(Attendance.student_id == student.id, Attendance.attendance_date == day))
        if existing:
            return existing, False
        raise
    db.refresh(row)
    return row, True
