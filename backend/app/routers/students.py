import re
import uuid
from pathlib import Path
from typing import Annotated

import cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..config import get_settings
from ..cv.face_engine import FaceEngine, FaceProcessingError, decode_image
from ..cv.matcher import serialize_embedding
from ..database import get_db
from ..models import Role, Student, User
from ..schemas import StudentOut

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentOut, status_code=201)
async def register_student(
    student_id: Annotated[str, Form()], name: Annotated[str, Form()], department: Annotated[str, Form()],
    year: Annotated[int, Form()], photo: Annotated[UploadFile, File()], db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(Role.ADMIN))],
) -> Student:
    if db.scalar(select(Student).where(Student.student_id == student_id.strip())):
        raise HTTPException(409, "Student ID already exists")
    if year < 1 or year > 8:
        raise HTTPException(422, "Year must be between 1 and 8")
    try:
        data = await photo.read()
        image = decode_image(data)
        face = FaceEngine.instance().extract_one(image)
    except FaceProcessingError as exc:
        raise HTTPException(422, str(exc))
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", student_id)[:64]
    relative = Path("students") / f"{safe_id}_{uuid.uuid4().hex[:8]}.jpg"
    destination = get_settings().upload_path / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destination), image):
        raise HTTPException(500, "Could not save the registered photograph")
    student = Student(student_id=student_id.strip(), name=name.strip(), department=department.strip(), year=year, photo_path=relative.as_posix(), face_embedding=serialize_embedding(face.embedding))
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("", response_model=list[StudentOut])
def list_students(db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.ADMIN, Role.PROFESSOR))]) -> list[Student]:
    return list(db.scalars(select(Student).order_by(Student.name)))


@router.delete("/{student_pk}", status_code=204)
def delete_student(student_pk: int, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(require_roles(Role.ADMIN))]) -> None:
    student = db.get(Student, student_pk)
    if not student:
        raise HTTPException(404, "Student not found")
    db.delete(student)
    db.commit()
