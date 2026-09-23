# Smart ID Attendance System

Smart ID Attendance is a local university attendance application that identifies a registered student from the face printed on an ID card. It uses a React frontend, a FastAPI backend, SQLite, OpenCV, InsightFace with an ArcFace-compatible model, ONNX Runtime, and optional Ultralytics YOLO ID-card detection.

The application has three roles:

- **Admin:** register students and create or delete professor accounts.
- **Guard:** capture or upload a student ID image and record attendance.
- **Professor:** review, filter, summarize, and export attendance records.

All recognition and data storage run locally. The project does not use cloud recognition, paid APIs, OCR, or QR codes.

For implementation details, diagrams, database design, API documentation, and security notes, read the [complete project documentation](docs/PROJECT_DOCUMENTATION.md).

## Contents

1. [Linux requirements](#linux-requirements)
2. [Clone the repository](#clone-the-repository)
3. [Install Linux system packages](#install-linux-system-packages)
4. [Create the Python virtual environment](#create-the-python-virtual-environment)
5. [Install the complete backend stack](#install-the-complete-backend-stack)
6. [Configure the backend](#configure-the-backend)
7. [Initialize the database](#initialize-the-database)
8. [Install the frontend](#install-the-frontend)
9. [Run the application](#run-the-application)
10. [Development accounts](#development-accounts)
11. [How to use the application](#how-to-use-the-application)
12. [Verify the installation](#verify-the-installation)
13. [Stop and restart the application](#stop-and-restart-the-application)
14. [Run tests and production build](#run-tests-and-production-build)
15. [Troubleshooting](#troubleshooting)

## Linux requirements

The tested development setup uses:

| Requirement | Version or purpose |
|---|---|
| Linux | Ubuntu/Debian-style native Linux system |
| Python | Python 3.11 |
| Node.js | Node 20 or newer |
| npm | Installed with Node.js |
| Git | Repository checkout and updates |
| Disk space | At least 2–3 GB for environments, packages, and models |
| Camera | Optional; an image can be uploaded instead |

This project uses a standard virtual environment at `backend/.venv`. Conda is not used for the project. If your terminal displays `(base)`, you may leave it active because the commands below explicitly activate and use `backend/.venv`.

Check the installed tools:

```bash
git --version
python3.11 --version
node --version
npm --version
```

Expected major versions:

```text
Python 3.11.x
Node.js 20.x or newer
```

If `python3.11` is not available in your distribution, install Python 3.11 using your normal system Python manager before continuing. Ubuntu 24.04 does not include Python 3.11 in its default package set, so do not replace the commands with Python 3.12: the tested backend environment is Python 3.11.

## Clone the repository

For a new checkout:

```bash
mkdir -p ~/than
cd ~/than
git clone https://github.com/tomgumR/smart-id-attendance-system.git
cd smart-id-attendance-system
```

On the machine where this project is already configured, the repository is located at:

```text
/home/tammy-ralte/than/smart-id-attendance-system
```

If the repository already exists, do not clone it again. Enter the existing directory:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system
```

## Install Linux system packages

Install the compiler and shared libraries commonly needed by InsightFace and OpenCV:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  pkg-config \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender1
```

If your system provides Python 3.11 packages, also ensure the virtual-environment and development packages are installed:

```bash
sudo apt install -y python3.11-venv python3.11-dev
```

Skip that second command when Python 3.11 was installed using another manager and already supports `python3.11 -m venv`.

## Create the Python virtual environment

Move into the backend directory:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
```

Create the project-local environment:

```bash
python3.11 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, the terminal prompt normally starts with `(.venv)`. Confirm that the environment uses Python 3.11:

```bash
python --version
which python
```

The second command should point inside:

```text
.../smart-id-attendance-system/backend/.venv/bin/python
```

Upgrade the Python packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Existing configured checkout

The current machine already has `backend/.venv`. Do not recreate it each time. Activate it with:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
source .venv/bin/activate
```

## Install the complete backend stack

Install CPU-only PyTorch first. This prevents pip from downloading large CUDA packages that are unnecessary for this CPU configuration:

```bash
python -m pip install \
  "torch==2.5.1+cpu" \
  "torchvision==0.20.1+cpu" \
  --index-url https://download.pytorch.org/whl/cpu
```

Then install the complete project requirements:

```bash
python -m pip install -r requirements.txt
```

The full requirements include:

- FastAPI and Uvicorn;
- SQLAlchemy and SQLite support;
- Argon2 and JWT authentication;
- OpenCV and NumPy;
- ONNX Runtime;
- InsightFace;
- Ultralytics/YOLO;
- pytest and HTTPX.

Do not use `requirements-core.txt` for the working application. The complete InsightFace computer-vision pipeline requires `requirements.txt`.

Confirm the main packages import from the virtual environment:

```bash
python -c "import cv2, torch, onnxruntime, insightface, ultralytics; print('CV dependencies imported successfully'); print('PyTorch:', torch.__version__); print('CUDA enabled:', torch.cuda.is_available()); print('ONNX providers:', onnxruntime.get_available_providers())"
```

For the intended CPU setup, `torch.cuda.is_available()` should print `False`, and the ONNX providers should include `CPUExecutionProvider`.

## Configure the backend

Remain in the `backend` directory and create the local configuration file:

```bash
cp .env.example .env
```

Do not overwrite an existing `.env` unless you intend to reset its local settings.

The default development configuration is:

```dotenv
DATABASE_URL=sqlite:///./smart_attendance.db
JWT_SECRET=replace-with-a-long-random-secret
FACE_MATCH_THRESHOLD=0.45
INSIGHTFACE_MODEL_ROOT=models/insightface
YOLO_MODEL_PATH=models/id_card.pt
UPLOAD_DIRECTORY=uploads
ALLOW_MANUAL_ID_FALLBACK=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Generate a suitable local JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value and replace `replace-with-a-long-random-secret` in `.env`.

### Important paths

All relative backend paths are resolved from the `backend` directory:

| Item | Default location |
|---|---|
| SQLite database | `backend/smart_attendance.db` |
| Registered photographs | `backend/uploads/students/` |
| InsightFace model root | `backend/models/insightface/` |
| Expected `buffalo_l` model | `backend/models/insightface/models/buffalo_l/` |
| Optional custom YOLO weights | `backend/models/id_card.pt` |

The database, `.env`, uploads, downloaded models, and virtual environments are excluded from Git.

## Initialize the database

With `backend/.venv` activated and the current directory set to `backend`, run:

```bash
python ../scripts/seed_database.py
```

This command:

1. creates the SQLite database when it does not exist;
2. creates the application tables;
3. creates or updates the three development accounts;
4. hashes account passwords with Argon2.

The seed command can be run more than once. Running it again resets the seeded accounts to the development passwords listed below.

Confirm that the database exists:

```bash
ls -lh smart_attendance.db
```

## Install the frontend

Open a terminal and enter the frontend directory:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/frontend
```

### Standard Node.js installation

If `node` and `npm` are installed system-wide:

```bash
npm install
```

This installs the versions recorded in `package-lock.json` into `frontend/node_modules`.

### Existing configured checkout on this machine

This checkout also has a project-local Node.js runtime in `frontend/.node`. Add it to the current terminal's `PATH`:

```bash
export PATH="$PWD/.node/bin:$PATH"
node --version
npm --version
npm install
```

The `export` command affects only the current terminal. Run it again in a new frontend terminal before using `npm` when a system-wide Node.js installation is unavailable.

## Run the application

The backend and frontend are two separate development servers. Open **two normal terminals** and keep both terminals open while using the application.

You may leave Conda `(base)` active because Terminal 1 explicitly activates the project-local `.venv`.

### Terminal 1 — Backend

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

A successful startup includes output similar to:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal open.

### Terminal 2 — Frontend

For the existing local Node.js runtime:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/frontend
export PATH="$PWD/.node/bin:$PATH"
npm run dev -- --host 127.0.0.1
```

If Node.js is installed system-wide, the `export PATH=...` line is not required:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/frontend
npm run dev -- --host 127.0.0.1
```

A successful startup includes:

```text
Local: http://127.0.0.1:5173/
```

Keep this terminal open.

### Open the application

Open these addresses in a browser:

- Application: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- Backend health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Use the same hostname consistently. The project accepts both `localhost` and `127.0.0.1`, but the commands above deliberately use `127.0.0.1` everywhere.

## Development accounts

The seed script creates these local development accounts:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Guard | `guard1` | `guard123` |
| Professor | `professor1` | `professor123` |

On the login page:

1. choose the correct role;
2. enter the matching username and password;
3. click **Sign in**.

The selected role is enforced by the backend. For example, the admin credentials are rejected from the Professor Login form even when the username and password are correct.

These accounts are for local development only. Change their passwords before exposing the application to other machines or users.

## How to use the application

### Admin workflow

1. Choose **Admin** on the login page.
2. Sign in with an admin account.
3. Use the **Students** tab to register a student.
4. Enter student ID, name, department, and academic year.
5. Upload one clear, front-facing photograph containing exactly one face.
6. Click **Register student**.
7. Use the **Professors** tab to create or delete professor accounts.

Student registration initializes InsightFace when the model has not yet been loaded. The first request may take longer while `buffalo_l` is loaded or downloaded.

### Guard workflow

1. Choose **Guard** on the login page.
2. Sign in with a security account.
3. Click **Start camera** and allow browser camera access.
4. Hold the student ID close to the camera so the printed face is clear.
5. Click **Verify & mark present**.

Alternatively, click **Upload ID** and select an ID-card image before verifying.

If custom YOLO weights are not present, the entire camera frame is treated as an already cropped ID card. The card should fill most of the frame. A successful match creates one attendance record for the student for the current day. A repeated scan returns `DUPLICATE` instead of creating another record.

### Professor workflow

1. Choose **Professor** on the login page.
2. Sign in with a professor account.
3. Review registered, present, absent, and attendance-percentage totals.
4. Search by student name or ID.
5. Filter by department or date range.
6. Click **Apply** to load filtered results.
7. Click **Export CSV** to download the filtered attendance records.

## Verify the installation

### Check the backend

With the backend running:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and confirm that the FastAPI documentation loads.

### Check the frontend

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The page should show **Smart ID Attendance** and the Admin, Guard, and Professor role choices.

### Check authentication

Test each development account through its matching role form. A successful login should open:

| Role | Expected screen |
|---|---|
| Admin | Student/Professor registry |
| Guard | Attendance scanner |
| Professor | Attendance dashboard |

### Check the computer-vision environment

From `backend/` with `.venv` active:

```bash
python -c "import cv2, torch, onnxruntime, insightface, ultralytics; print('OpenCV', cv2.__version__); print('PyTorch', torch.__version__); print('ONNX Runtime', onnxruntime.__version__); print('InsightFace', insightface.__version__); print('Ultralytics', ultralytics.__version__)"
```

Package imports confirm installation. Registering a student with a real photograph additionally confirms that InsightFace initializes, detects a face, and generates an embedding.

## Stop and restart the application

### Stop

In the backend terminal, press:

```text
Ctrl+C
```

In the frontend terminal, press:

```text
Ctrl+C
```

### Restart later

You do not need to reinstall dependencies, recreate `.venv`, reseed the database, or run `npm install` every time.

Start the backend again:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/frontend
export PATH="$PWD/.node/bin:$PATH"
npm run dev -- --host 127.0.0.1
```

## Run tests and production build

### Backend tests

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
source .venv/bin/activate
python -m pytest -q
```

### Frontend production build

```bash
cd /home/tammy-ralte/than/smart-id-attendance-system/frontend
export PATH="$PWD/.node/bin:$PATH"
npm run build
```

The production bundle is written to `frontend/dist/`.

## Troubleshooting

### Login displays `Failed to fetch`

This means the browser could not complete the API request. Check all of the following:

1. The backend terminal is still running.
2. [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) returns `{"status":"ok"}`.
3. The frontend was opened at `http://127.0.0.1:5173`.
4. `.env` contains both local frontend origins:

   ```dotenv
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

5. Restart the backend after changing `.env`.

### Login says the account is not authorized for the selected role

Return to **Choose another role** and select the role matching the account. Role selection is enforced server-side.

### `python3.11: command not found`

Install Python 3.11 with your system Python manager. Do not create this tested environment using Python 3.12 and do not switch the project to Conda.

### InsightFace fails to install

Confirm the compiler packages are installed, activate `.venv`, upgrade pip/build tools, and retry:

```bash
sudo apt install -y build-essential cmake pkg-config python3.11-dev
cd /home/tammy-ralte/than/smart-id-attendance-system/backend
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### InsightFace model is unavailable

The expected model directory is:

```text
backend/models/insightface/models/buffalo_l/
```

Ensure the machine has internet access for the first model download or place the `buffalo_l` model pack at that location. Recognition uses ONNX Runtime's CPU provider after the model is available.

### Pip starts downloading large NVIDIA/CUDA packages

Cancel the installation and install the CPU-only PyTorch wheels first:

```bash
python -m pip install \
  "torch==2.5.1+cpu" \
  "torchvision==0.20.1+cpu" \
  --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
```

### Camera permission is denied

Allow camera permission for `http://127.0.0.1:5173`. If a camera is unavailable, use **Upload ID** instead.

### No face is detected

Use a clear image with one front-facing face. Avoid glare, blur, shadows, very small faces, and images containing multiple people.

### Verification uses the full-image fallback

The repository does not include a trained custom `backend/models/id_card.pt`. With `ALLOW_MANUAL_ID_FALLBACK=true`, the full image is processed as an already cropped card. Hold the ID close to the camera or upload a tightly cropped ID image.

Instructions for training optional YOLO card-detector weights are in [training/yolo/README.md](training/yolo/README.md).

### Port already in use

Check which process is using a port:

```bash
ss -ltnp | grep -E ':8000|:5173'
```

Stop the old development process or press `Ctrl+C` in the terminal where it is running, then start the application again.

## Local data and privacy

Registered photographs and face embeddings are biometric data. Obtain informed consent, limit access to the computer and project directories, define a deletion policy, and follow applicable university and privacy requirements.

Before exposing the application beyond a private local demonstration:

- replace the development JWT secret;
- change all seeded passwords;
- use HTTPS;
- restrict database and upload-directory permissions;
- calibrate the face threshold using representative validation data;
- review the licensing terms of the InsightFace model pack.

The current system is a local classroom prototype and should not be used for consequential surveillance decisions.
