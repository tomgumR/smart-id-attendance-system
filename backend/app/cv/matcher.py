from dataclasses import dataclass

import numpy as np

from ..models import Student


def serialize_embedding(value: np.ndarray) -> bytes:
    return np.asarray(value, dtype=np.float32).tobytes()


def deserialize_embedding(value: bytes) -> np.ndarray:
    embedding = np.frombuffer(value, dtype=np.float32).copy()
    embedding /= max(float(np.linalg.norm(embedding)), 1e-12)
    return embedding


@dataclass
class Match:
    student: Student | None
    score: float | None
    second_best: float | None


def identify(query: np.ndarray, students: list[Student], threshold: float) -> Match:
    if not students:
        return Match(None, None, None)
    scored = sorted(
        ((float(np.dot(query, deserialize_embedding(student.face_embedding))), student) for student in students),
        key=lambda item: item[0], reverse=True,
    )
    best_score, best_student = scored[0]
    second = scored[1][0] if len(scored) > 1 else None
    return Match(best_student if best_score >= threshold else None, best_score, second)


def similarity(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.dot(first, second))
