# Smart ID-Based Face Recognition Attendance System

A local BTech classroom prototype that identifies a student from the **face printed on an ID card** and records attendance. It does not use OCR, QR codes, paid APIs, or cloud recognition.

For an implementation-level explanation of the architecture, database, API, role flows, computer-vision pipeline, configuration, testing, security, and troubleshooting, see the [complete project documentation](docs/PROJECT_DOCUMENTATION.md).

## Architecture

`React webcam/upload → FastAPI → YOLO ID crop (or declared fallback) → InsightFace detection/alignment + ArcFace embedding → cosine 1:N search → SQLite attendance`

The backend enforces ADMIN, SECURITY, and PROFESSOR permissions. Passwords use Argon2 and API sessions use signed JWTs. A database unique constraint prevents duplicate attendance for the same student and calendar day, even under concurrent requests.

## Roles and account management

The entry screen asks the user to choose **Admin**, **Guard**, or **Professor** before signing in. The backend validates the selected role as part of authentication, so an account cannot sign in through another role's form.

- **Admin:** register students and manage professor accounts from separate registry tabs. Professor passwords are hashed by the existing Argon2 authentication service and are never returned by the API.
- **Guard:** scan or upload student ID-card images and record attendance.
- **Professor:** review attendance records and summary data.

Administrators can create a professor with a username and password, view all professor accounts, and delete a professor. Deleting the account immediately prevents further login with those credentials. These operations use the existing RBAC-protected `/api/admin` endpoints.

## Project layout

```text
backend/app/       API, auth, models, services, isolated CV pipeline
backend/tests/     auth, matcher, and duplicate-prevention tests
frontend/src/      role-based React dashboards and webcam capture
scripts/           development account seeding
training/yolo/     dataset example, trainer, and evaluation instructions
```

## Install and run on Linux

Requirements: Python 3.11, Node 20+, a webcam for ID-card capture, and roughly 2 GB free for the CV packages and model pack. The commands below use a standard project-local Python virtual environment; Conda is not required.

```bash
cd smart-id-attendance-system/backend
python3.11 -m venv .venv
source .venv/bin/activate

# Install CPU-only PyTorch first so Ultralytics does not pull CUDA packages.
python -m pip install "torch==2.5.1+cpu" "torchvision==0.20.1+cpu" \
  --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt

cp .env.example .env
# Replace JWT_SECRET in .env with a long random value before sharing the app.
python ../scripts/seed_database.py
uvicorn app.main:app --reload
```

Ubuntu 24.04 may not provide Python 3.11 in its default repositories. Install Python 3.11 with your normal system Python manager first, then run the same `python3.11 -m venv .venv` command. The development environment used to verify this repository uses a standalone Python 3.11 runtime under `backend/.python-builds` only as the base interpreter for the standard `backend/.venv`; both directories are ignored by Git.

In another terminal:

```bash
cd smart-id-attendance-system/frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Development-only accounts are `admin/admin123`, `guard1/guard123`, and `professor1/professor123`. Change them whenever this prototype is exposed beyond a private demo. API documentation is at `http://localhost:8000/docs`.

The first registration or verification initializes InsightFace `buffalo_l`. Its model pack is downloaded to `backend/models/insightface/models/buffalo_l`, controlled by `INSIGHTFACE_MODEL_ROOT`. If automatic download is unavailable, obtain the model through the InsightFace project’s documented model zoo and place it there. Check the model/package licensing for the intended use; pretrained research models may have non-commercial research restrictions. After the model is present, recognition runs locally with ONNX Runtime's CPU provider and has no per-request cost.

The repository does not include trained `models/id_card.pt` weights. With the default `ALLOW_MANUAL_ID_FALLBACK=true`, verification expects a tightly cropped card image and still performs real InsightFace detection and ArcFace embedding. Train or supply the documented YOLO weights for ID-card detection in wider scene images.

## Install and run on Windows

```powershell
cd smart-id-attendance-system/backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python ../scripts/seed_database.py
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd smart-id-attendance-system/frontend
npm install
npm run dev
```

On Windows, `insightface` is distributed as source and may require Visual Studio C++ Build Tools with the Windows 10/11 SDK. The complete face-recognition pipeline requires `requirements.txt`; `requirements-core.txt` is only an API-shell troubleshooting option and does not provide face recognition.

## Demo workflow

1. Choose **Admin**, sign in, and use the **Students** registry to register 5–20 students with clear, front-facing, consented photographs. Images with zero or multiple faces are rejected. Use the **Professors** registry to create or delete professor login accounts.
2. Sign in as guard, start the webcam, center the card, and verify. The upload control supports development without a webcam.
3. Without custom YOLO weights the whole image is deliberately treated as an already-cropped ID; the result message explicitly says the fallback was used. This is suitable for uploaded, tightly cropped card photographs—not a claim of card detection.
4. Sign in as professor to filter records, inspect scores and methods, and export CSV.

For direct testing, use `POST /api/verification/id-image` with multipart field `image`. Send the JWT as `Authorization: Bearer …`.

## Face matching and calibration

InsightFace detects landmarks, aligns the face, and returns an ArcFace-style normalized embedding. Embeddings are stored as float32 bytes in SQLite. Matching computes cosine similarity against every registered embedding. `FACE_MATCH_THRESHOLD` defaults to **0.45 only as a starting demo value**; it is not universally optimal and must be calibrated on representative validation data.

Create a consented CSV with `score,label` columns (`1` same identity, `0` different) and run:

```bash
python -m app.evaluation pairs.csv --start 0.1 --stop 0.8 --step 0.01 > metrics.csv
```

This reports accuracy, precision, recall, FAR, FRR, TPR, and FPR across thresholds; TPR/FPR form the ROC curve. Keep a held-out test set. Evaluate normal, rotated, near/far, low-light, glare, occluded, and changed-photo conditions. YOLO training and its precision/recall/mAP reporting are documented in `training/yolo/README.md`.

## Configuration

Copy `backend/.env.example`. Set `DATABASE_URL`, a long random `JWT_SECRET`, `FACE_MATCH_THRESHOLD`, `INSIGHTFACE_MODEL_ROOT`, `YOLO_MODEL_PATH`, `UPLOAD_DIRECTORY`, `ALLOW_MANUAL_ID_FALLBACK`, and allowed frontend origins. Secrets, model downloads, and biometric uploads are git-ignored.

## Tests and build

```bash
cd backend
.venv/bin/python -m pytest -q
cd ../frontend
npm run build
```

## Known limitations and privacy

- This is a CPU-oriented classroom prototype. Linear 1:N search is appropriate for a small university demo, not a large identity service.
- The fallback expects the card to fill the image. Train the supplied YOLO pipeline for robust scene detection.
- Daily duplicate prevention uses the application/host calendar. Formal class sessions, course enrollment, audit trails, account deactivation, and timezone administration are future work.
- Face recognition can exhibit demographic and capture-condition bias. Measure subgroup performance, obtain informed consent, minimize retention, encrypt/limit access to the database and uploads, publish a deletion process, and follow applicable biometric/privacy law. Never use the demo for consequential surveillance decisions.
