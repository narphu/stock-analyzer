# 🛠️ Developer Guide – Stock Analyzer (Local Setup)

This guide outlines how to set up, develop, and deploy both the frontend and backend components, train models, and build Docker images for this project.

It includes:

- ✅ Python backend (FastAPI + Prophet)
- ✅ React frontend (Vite + Chakra)
- ✅ Makefile-based automation

---

## ⚙️ Requirements

- Python 3.8+  
- Node.js 18+ (recommended via [nvm](https://github.com/nvm-sh/nvm))  
- `make`  
- Internet connection for downloading data from yfinance

---

## 🧾 Project Structure

```
stock-analyzer/
├── backend/                # FastAPI + Prophet models
│   ├── main.py
│   ├── train_model.py
│   
├── frontend/               # Vite + React + Tailwind
│   ├── src/App.jsx
│   └── package.json
|__ ml
|  ├── models/              # Pretrained .pkl models
├── Makefile                # All local automation targets
└── DEVELOPER.md            # This file
```

---

## 🚀 Quick Start (Recommended)

From the project root:

```bash
# Install Python and Node dependencies
make venv
make deps
make frontend-deps

# Pretrain stock models
make train-models

# Run with docker compose
make docker-up
```

### Run backend and frontend in separate terminals
``` bash
make dev          # Terminal 1 - FastAPI backend on http://localhost:8000
make frontend     # Terminal 2 - React frontend on http://localhost:5173
```

---

## 🐍 Backend – Python (FastAPI + Prophet)

### Run manually:
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
python backend/train_model.py      # Train models
uvicorn backend.main:app --reload  # Run API at http://localhost:8000
```

### Health Check

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok"}
```

### Sample Prediction

```bash
curl -X POST http://127.0.0.1:8000/predict   -H "Content-Type: application/json"   -d '{"ticker": "AAPL"}'
```


## 🐍 Python Backend

### Setup Virtual Environment

```bash
make venv
```

Creates a virtual environment under `backend/venv` and installs dependencies.

### Run Backend in Dev Mode

```bash
make backend-dev
```

Runs FastAPI using Uvicorn with `USE_LOCAL_MODELS=true` for loading models locally.

### Install/Update Dependencies

```bash
make deps
```

Upgrade pip and reinstall Python packages.

### Freeze Dependencies

```bash
make freeze
```

Writes current dependencies to `requirements.txt`.

### Run Backend Tests

```bash
make test-backend
```

Executes `pytest` tests in the `backend/tests` directory.

---

## Model Training

### Train All Models Locally

```bash
make train-models
```

Creates a virtual env under `ml/venv`, installs ML dependencies, and runs `ml/train_model.py`. Trained models saved locally or uploaded depending on configuration.

---

## React Frontend

### Install Node Modules

```bash
make frontend-deps
```

Installs frontend packages under `frontend/node_modules`.

### Start Local Dev Server

```bash
make frontend
```

Runs `npm run dev` inside the `frontend` directory.

### Build Static Files

```bash
make frontend-build
```

Runs `npm run build` to generate static files in `frontend/dist`.

### Upload to S3

```bash
make frontend-upload
```

Syncs the `dist/` folder with your S3 bucket (`shrubb-stock-analyzer-frontend`).

### Build + Upload in One

```bash
make frontend-deploy
```

Builds and deploys frontend in one go.

### Clean Build Output

```bash
make frontend-clean
```

Removes the contents of `frontend/dist`.

---

## 🐳 Docker

### Local Docker Dev Environment

```bash
make docker-up
```

Builds and starts the app using `docker-compose`.

### Shutdown and Cleanup

```bash
make docker-down
```

Stops and removes containers and volumes.

### Rebuild Containers

```bash
make docker-rebuild
```

Stops, rebuilds, and restarts containers.

---

## ☁️ AWS & ECR

### Build Backend Image

```bash
make build-backend-prod
```

Builds a production image for the backend using `backend/Dockerfile.prod`.

### Push Backend to ECR

```bash
make push-backend
```

Builds and pushes the backend image tagged as `v0.0.8`.

---

## 🧠 SageMaker Custom Model Image

### Build Training Image Locally

```bash
make ml-image-build
```

Creates a Docker image from `ml/Dockerfile` for SageMaker training jobs.

### Push to ECR

```bash
make ml-image-push
```

Tags and pushes the ML image to ECR under `stock-analyzer-shrubb-ai-custom-trainer:v0.0.4`.

---

## 🧱 Infrastructure (Terraform)

### Apply Terraform Config

```bash
make tf-apply
```

Runs `terraform init` and `terraform apply` with the current backend image version as a variable.

---

## 🧼 Clean Project

```bash
make clean
```

Removes all caches, pyc files, and virtual environments.

---

For full details on architecture and model usage, see [`README.md`](README.md).
