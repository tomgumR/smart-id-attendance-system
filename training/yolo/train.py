"""Train a custom ID-card detector with Ultralytics YOLO."""
from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).parent
model = YOLO("yolo11n.pt")
model.train(data=str(ROOT / "dataset.yaml"), epochs=80, imgsz=640, batch=16, project=str(ROOT / "runs"), name="id_card")
model.val()
