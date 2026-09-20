import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    SECURITY = "SECURITY"
    PROFESSOR = "PROFESSOR"


class VerificationMode(str, enum.Enum):
    ID_ONLY = "ID_ONLY"
    ID_LIVE = "ID_LIVE"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    department: Mapped[str] = mapped_column(String(120), index=True)
    year: Mapped[int] = mapped_column(Integer)
    photo_path: Mapped[str] = mapped_column(String(500))
    face_embedding: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    attendance: Mapped[list["Attendance"]] = relationship(back_populates="student")

    @property
    def photo_url(self) -> str:
        return f"/uploads/{self.photo_path}"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "attendance_date", name="uq_student_attendance_day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    attendance_date: Mapped[str] = mapped_column(String(10), index=True)
    verification_mode: Mapped[VerificationMode] = mapped_column(Enum(VerificationMode))
    similarity_score: Mapped[float] = mapped_column(Float)
    live_similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    security_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    student: Mapped[Student] = relationship(back_populates="attendance")
    security_user: Mapped[User] = relationship()
