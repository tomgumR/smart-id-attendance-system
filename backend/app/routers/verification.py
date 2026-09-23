from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..config import get_settings
from ..cv.face_engine import FaceEngine, FaceProcessingError, decode_image
from ..cv.id_detector import IdCardDetector
from ..cv.matcher import identify
from ..database import get_db
from ..models import Role, Student, User
from ..schemas import StudentOut, VerificationResult
from ..services import attendance_to_dict, record_attendance

router = APIRouter(prefix="/verification", tags=["verification"])


def process_id(data: bytes, db: Session):
    settings = get_settings()
    image = decode_image(data)
    detector = IdCardDetector(settings.yolo_model_path, settings.allow_manual_id_fallback)
    card, _, fallback = detector.crop(image)
    face = FaceEngine.instance().extract_one(card)
    match = identify(face.embedding, list(db.scalars(select(Student))), settings.face_match_threshold)
    return match, fallback


@router.post("/id-image", response_model=VerificationResult)
async def verify_id_image(
    image: Annotated[UploadFile, File()], db: Annotated[Session, Depends(get_db)],
    guard: Annotated[User, Depends(require_roles(Role.SECURITY, Role.ADMIN))],
) -> VerificationResult:
    try:
        match, fallback = process_id(await image.read(), db)
    except FaceProcessingError as exc:
        raise HTTPException(422, str(exc))
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    fallback_note = " Full-image development fallback was used." if fallback else ""
    if not match.student:
        return VerificationResult(status="UNKNOWN", message=f"Unknown person: similarity did not pass the configured threshold.{fallback_note}", similarity_score=match.score, second_best_score=match.second_best)
    row, created = record_attendance(db, match.student, guard, match.score or 0.0)
    return VerificationResult(
        status="RECORDED" if created else "DUPLICATE",
        message=("Attendance recorded." if created else f"Attendance already recorded at {row.timestamp:%H:%M}.") + fallback_note,
        student=StudentOut.model_validate(match.student), similarity_score=match.score,
        second_best_score=match.second_best, attendance=attendance_to_dict(row),
    )
