# Smart ID-Based Face Recognition Attendance System

A local BTech classroom prototype that identifies a student from the **face printed on an ID card**, optionally compares a live face, and records attendance. It does not use OCR, QR codes, paid APIs, or cloud recognition.

## Architecture

`React webcam/upload → FastAPI → YOLO ID crop (or declared fallback) → InsightFace detection/alignment + ArcFace embedding → cosine 1:N search → optional live 1:1 verification → SQLite attendance`

The backend enforces ADMIN, SECURITY, and PROFESSOR permissions. Passwords use Argon2 and API sessions use signed JWTs. A database unique constraint prevents duplicate attendance for the same student and calendar day, even under concurrent requests.

## Project layout

```text
backend/app/       API, auth, models, services, isolated CV pipeline
backend/tests/     auth, matcher, and duplicate-prevention tests
frontend/src/      role-based React dashboards and webcam capture
scripts/           development account seeding
training/yolo/     dataset example, trainer, and evaluation instructions
```

## Install and run

Requirements: Python 3.11, Node 20+, a webcam for live capture, and roughly 1–2 GB free for CV packages/models.

```powershell
cd smart-attendance/backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python ../scripts/seed_database.py
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd smart-attendance/frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Development-only accounts are `admin/admin123`, `guard1/guard123`, and `professor1/professor123`. Change them whenever this prototype is exposed beyond a private demo. API documentation is at `http://localhost:8000/docs`.

The first registration/verification initializes InsightFace `buffalo_l`. InsightFace normally obtains its model pack on first use. If automatic download is unavailable, obtain the model through the InsightFace project’s documented model zoo and place it in `~/.insightface/models/buffalo_l`. Check the model/package licensing for the intended use; pretrained research models may have non-commercial research restrictions. After the model is present, operation is local and has no per-request cost.

On Windows, `insightface` is distributed as source and may require Visual Studio C++ Build Tools with the Windows 10/11 SDK. If that native build is not available, install and test the API shell with `pip install -r requirements-core.txt`; registration and verification intentionally return a clear model-unavailable error until the CV requirements and model pack are installed. WSL/Linux is usually the simplest environment for the complete CV stack.

## Demo workflow

1. Sign in as admin and register 5–20 students using clear, front-facing, consented photographs. Images with zero or multiple faces are rejected.
2. Sign in as guard, choose **ID only** (default) or **ID + live face**, start the webcam, center the card, and verify. Upload controls support development without a webcam.
3. Without custom YOLO weights the whole image is deliberately treated as an already-cropped ID; the result message explicitly says the fallback was used. This is suitable for uploaded, tightly cropped card photographs—not a claim of card detection.
4. Sign in as professor to filter records, inspect scores and methods, and export CSV.

For direct testing, use `POST /api/verification/id-image` with multipart field `image`, or `/api/verification/id-live` with `id_image` and `live_image`. Send the JWT as `Authorization: Bearer …`.

## Face matching and calibration

InsightFace detects landmarks, aligns the face, and returns an ArcFace-style normalized embedding. Embeddings are stored as float32 bytes in SQLite. Matching computes cosine similarity against every registered embedding. `FACE_MATCH_THRESHOLD` and `LIVE_FACE_THRESHOLD` default to **0.45 only as starting demo values**; they are not universally optimal and must be calibrated on representative validation data.

Create a consented CSV with `score,label` columns (`1` same identity, `0` different) and run:

```powershell
python -m app.evaluation pairs.csv --start 0.1 --stop 0.8 --step 0.01 > metrics.csv
```

This reports accuracy, precision, recall, FAR, FRR, TPR, and FPR across thresholds; TPR/FPR form the ROC curve. Keep a held-out test set. Evaluate normal, rotated, near/far, low-light, glare, occluded, and changed-photo conditions. YOLO training and its precision/recall/mAP reporting are documented in `training/yolo/README.md`.

## Configuration

Copy `backend/.env.example`. Set `DATABASE_URL`, a long random `JWT_SECRET`, both face thresholds, `YOLO_MODEL_PATH`, `UPLOAD_DIRECTORY`, `ALLOW_MANUAL_ID_FALLBACK`, and allowed frontend origins. Secrets and biometric uploads are git-ignored.

## Tests and build

```powershell
cd backend; pytest -q
cd ../frontend; npm run build
```

## Known limitations and privacy

- This is a CPU-oriented classroom prototype. Linear 1:N search is appropriate for a small university demo, not a large identity service.
- The fallback expects the card to fill the image. Train the supplied YOLO pipeline for robust scene detection.
- “ID + live” compares a second face frame but is **not liveness/anti-spoofing**; a photograph attack remains possible.
- Daily duplicate prevention uses the application/host calendar. Formal class sessions, course enrollment, audit trails, account deactivation, and timezone administration are future work.
- Face recognition can exhibit demographic and capture-condition bias. Measure subgroup performance, obtain informed consent, minimize retention, encrypt/limit access to the database and uploads, publish a deletion process, and follow applicable biometric/privacy law. Never use the demo for consequential surveillance decisions.
