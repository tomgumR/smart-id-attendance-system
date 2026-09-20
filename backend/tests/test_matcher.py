import numpy as np

from app.cv.matcher import identify, serialize_embedding
from app.models import Student


def student(identifier, embedding):
    return Student(student_id=identifier, name=identifier, department="CSE", year=4, photo_path="x.jpg", face_embedding=serialize_embedding(np.array(embedding, dtype=np.float32)))


def test_identifies_best_cosine_match():
    students = [student("A", [1, 0]), student("B", [0, 1])]
    result = identify(np.array([0.99, 0.01], dtype=np.float32), students, 0.8)
    assert result.student.student_id == "A"
    assert result.second_best is not None


def test_rejects_below_threshold():
    result = identify(np.array([0, 1], dtype=np.float32), [student("A", [1, 0])], 0.5)
    assert result.student is None
