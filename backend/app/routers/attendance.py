import csv
import io
from datetime import date, datetime, time, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from ..auth import require_roles
from ..database import get_db
from ..models import Attendance, Role, Student, User
from ..schemas import AttendanceOut, DashboardSummary
from ..services import attendance_to_dict

router = APIRouter(prefix="/attendance", tags=["attendance"])


def filtered_query(search: str | None, department: str | None, start_date: date | None, end_date: date | None):
    query = select(Attendance).join(Attendance.student).options(joinedload(Attendance.student), joinedload(Attendance.security_user)).order_by(Attendance.timestamp.desc())
    if search:
        term = f"%{search}%"
        query = query.where(or_(Student.name.ilike(term), Student.student_id.ilike(term)))
    if department:
        query = query.where(Student.department == department)
    if start_date:
        query = query.where(Attendance.attendance_date >= start_date.isoformat())
    if end_date:
        query = query.where(Attendance.attendance_date <= end_date.isoformat())
    return query


@router.get("", response_model=list[AttendanceOut])
def list_attendance(
    db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.PROFESSOR, Role.ADMIN))],
    search: str | None = None, department: str | None = None, start_date: date | None = None,
    end_date: date | None = None, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
) -> list[dict]:
    rows = db.scalars(filtered_query(search, department, start_date, end_date).offset(offset).limit(limit)).all()
    return [attendance_to_dict(row) for row in rows]


@router.get("/today", response_model=list[AttendanceOut])
def today(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.SECURITY, Role.ADMIN))]) -> list[dict]:
    rows = db.scalars(filtered_query(None, None, date.today(), date.today()).limit(20)).all()
    return [attendance_to_dict(row) for row in rows]


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.PROFESSOR, Role.ADMIN))], day: date = Query(default_factory=date.today)) -> DashboardSummary:
    total = db.scalar(select(func.count(Student.id))) or 0
    present = db.scalar(select(func.count(Attendance.id)).where(Attendance.attendance_date == day.isoformat())) or 0
    return DashboardSummary(total_registered=total, present=present, absent=max(0, total - present), attendance_percentage=round((present / total * 100) if total else 0, 2))


@router.get("/export")
def export_csv(
    db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.PROFESSOR, Role.ADMIN))],
    search: str | None = None, department: str | None = None, start_date: date | None = None, end_date: date | None = None,
) -> StreamingResponse:
    rows = db.scalars(filtered_query(search, department, start_date, end_date)).all()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Name", "Department", "Date", "Time", "Verification Method", "ID Similarity", "Guard"])
    for row in rows:
        writer.writerow([row.student.student_id, row.student.name, row.student.department, row.timestamp.date(), row.timestamp.time().replace(microsecond=0), row.verification_mode.value, f"{row.similarity_score:.4f}", row.security_user.username])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=attendance.csv"})
