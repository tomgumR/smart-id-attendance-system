from pathlib import Path

import numpy as np


class IdCardDetector:
    """YOLO ID-card detector with an explicit full-image development fallback."""

    def __init__(self, model_path: str, allow_fallback: bool = True) -> None:
        self.model_path = Path(model_path)
        self.allow_fallback = allow_fallback
        self.model = None
        if self.model_path.exists():
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))

    @property
    def using_fallback(self) -> bool:
        return self.model is None

    def crop(self, image: np.ndarray) -> tuple[np.ndarray, tuple[int, int, int, int], bool]:
        height, width = image.shape[:2]
        if self.model is None:
            if not self.allow_fallback:
                raise ValueError("ID-card detector weights are not configured.")
            return image, (0, 0, width, height), True
        result = self.model.predict(image, verbose=False, conf=0.35)[0]
        if len(result.boxes) == 0:
            raise ValueError("No ID card was detected.")
        best = max(result.boxes, key=lambda box: float(box.conf[0]))
        x1, y1, x2, y2 = (int(v) for v in best.xyxy[0].tolist())
        pad_x, pad_y = int((x2 - x1) * 0.03), int((y2 - y1) * 0.03)
        x1, y1 = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2, y2 = min(width, x2 + pad_x), min(height, y2 + pad_y)
        return image[y1:y2, x1:x2], (x1, y1, x2, y2), False
