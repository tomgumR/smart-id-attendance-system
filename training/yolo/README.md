# ID-card detector training

Create `dataset/images/{train,val,test}` and matching `dataset/labels/{train,val,test}` folders. Each label is YOLO format: `0 x_center y_center width height`, normalized to 0–1. Use consented ID-card images, vary rotation, distance, lighting, glare, and partial occlusion, and redact unrelated personal data.

From the backend virtual environment run `python ../training/yolo/train.py`. Ultralytics prints precision, recall, mAP@0.5, and mAP@0.5:0.95. Copy `runs/id_card/weights/best.pt` to `backend/models/id_card.pt`, or set `YOLO_MODEL_PATH`. The application visibly uses its full-image development fallback until weights exist.
