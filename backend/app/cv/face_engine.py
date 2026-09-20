import threading
from dataclasses import dataclass

import cv2
import numpy as np


class FaceProcessingError(ValueError):
    """A user-correctable face image error."""


@dataclass
class FaceResult:
    embedding: np.ndarray
    bbox: tuple[int, int, int, int]


class FaceEngine:
    """Lazy InsightFace detector/alignment/ArcFace embedding adapter."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        try:
            from insightface.app import FaceAnalysis
            self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
        except Exception as exc:
            raise RuntimeError(
                "InsightFace models are unavailable. Install requirements and allow the first model download, "
                "or place the buffalo_l model under ~/.insightface/models."
            ) from exc

    @classmethod
    def instance(cls) -> "FaceEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def extract_one(self, image: np.ndarray) -> FaceResult:
        faces = self.app.get(image)
        if not faces:
            raise FaceProcessingError("No face was detected. Use a clear, front-facing image.")
        if len(faces) > 1:
            raise FaceProcessingError("Multiple faces were detected. Provide an image containing one face only.")
        face = faces[0]
        embedding = np.asarray(face.normed_embedding, dtype=np.float32)
        embedding /= max(float(np.linalg.norm(embedding)), 1e-12)
        x1, y1, x2, y2 = (int(v) for v in face.bbox)
        return FaceResult(embedding=embedding, bbox=(x1, y1, x2, y2))


def decode_image(data: bytes) -> np.ndarray:
    if not data:
        raise FaceProcessingError("The uploaded image is empty.")
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise FaceProcessingError("The uploaded file is not a valid image.")
    if image.shape[0] < 80 or image.shape[1] < 80:
        raise FaceProcessingError("The image is too small; use at least 80 x 80 pixels.")
    return image
