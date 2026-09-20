from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Role, VerificationMode


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Role
    created_at: datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role: Role


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: str
    name: str
    department: str
    year: int
    photo_url: str
    created_at: datetime


class AttendanceOut(BaseModel):
    id: int
    student_id: str
    name: str
    department: str
    timestamp: datetime
    verification_mode: VerificationMode
    similarity_score: float
    live_similarity_score: float | None
    security_username: str


class VerificationResult(BaseModel):
    status: str
    message: str
    student: StudentOut | None = None
    similarity_score: float | None = None
    second_best_score: float | None = None
    live_similarity_score: float | None = None
    attendance: AttendanceOut | None = None


class DashboardSummary(BaseModel):
    total_registered: int
    present: int
    absent: int
    attendance_percentage: float
