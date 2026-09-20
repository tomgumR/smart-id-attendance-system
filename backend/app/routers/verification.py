from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_roles
from ..config import get_settings
from ..cv.face_engine import FaceEngine, FaceProcessingError, decode_image
from ..cv.id_detector import IdCardDetector
from ..cv.matcher import deserialize_embedding, identify, similarity
from ..database import get_db
from ..models import Role, Student, User, VerificationMode
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
    row, created = record_attendance(db, match.student, guard, VerificationMode.ID_ONLY, match.score or 0.0)
    return VerificationResult(
        status="RECORDED" if created else "DUPLICATE",
        message=("Attendance recorded." if created else f"Attendance already recorded at {row.timestamp:%H:%M}.") + fallback_note,
        student=StudentOut.model_validate(match.student), similarity_score=match.score,
        second_best_score=match.second_best, attendance=attendance_to_dict(row),
    )


@router.post("/id-live", response_model=VerificationResult)
async def verify_id_and_live(
    id_image: Annotated[UploadFile, File()], live_image: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)], guard: Annotated[User, Depends(require_roles(Role.SECURITY, Role.ADMIN))],
) -> VerificationResult:
    try:
        match, fallback = process_id(await id_image.read(), db)
        if not match.student:
            return VerificationResult(status="UNKNOWN", message="The ID face did not match a registered student.", similarity_score=match.score, second_best_score=match.second_best)
        live = FaceEngine.instance().extract_one(decode_image(await live_image.read()))
    except (FaceProcessingError, ValueError) as exc:
        raise HTTPException(422, str(exc))
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    live_score = similarity(live.embedding, deserialize_embedding(match.student.face_embedding))
    if live_score < get_settings().live_face_threshold:
        return VerificationResult(status="LIVE_MISMATCH", message="Live face does not match the identified person.", student=StudentOut.model_validate(match.student), similarity_score=match.score, second_best_score=match.second_best, live_similarity_score=live_score)
    row, created = record_attendance(db, match.student, guard, VerificationMode.ID_LIVE, match.score or 0.0, live_score)
    note = " Full-image development fallback was used." if fallback else ""
    return VerificationResult(status="RECORDED" if created else "DUPLICATE", message=("Attendance recorded." if created else f"Attendance already recorded at {row.timestamp:%H:%M}.") + note, student=StudentOut.model_validate(match.student), similarity_score=match.score, second_best_score=match.second_best, live_similarity_score=live_score, attendance=attendance_to_dict(row))
