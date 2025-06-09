# 🛠️ Developer Guide – Stock Analyzer (Local Setup)

This guide walks you through running the stock analyzer app locally. It includes:

- ✅ Python backend (FastAPI + Prophet)
- ✅ React frontend (Vite + Tailwind)
- ✅ Makefile-based automation
- ✅ Manual commands (if needed)

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
│   ├── models/             # Pretrained .pkl models
├── frontend/               # Vite + React + Tailwind
│   ├── src/App.jsx
│   └── package.json
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

### Makefile targets:
```bash
make venv           # Create virtualenv
make deps           # Install backend dependencies
make train-models   # Train Prophet models into backend/models/
make dev            # Run backend with hot reload
```

---

## ⚛️ Frontend – React (Vite + TailwindCSS)

### Run manually:
```bash
cd frontend
npm install
npm run dev     # Open http://localhost:5173
```

### Makefile targets:
```bash
make frontend-deps   # Install frontend dependencies
make frontend        # Start dev server on port 5173
```

---

## 🛠️ Useful Make Targets

| Command            | Description                             |
|--------------------|-----------------------------------------|
| `make venv`        | Create Python virtualenv in `backend/`  |
| `make deps`        | Install backend Python dependencies     |
| `make frontend-deps` | Install React + Tailwind dependencies |
| `make train-models`| Pretrain Prophet models for tickers     |
| `make dev`         | Run FastAPI backend                     |
| `make frontend`    | Run React frontend                      |
| `make clean`       | Delete virtualenv and caches            |

---

## Run with Docker Compose

### Start both the servers
``` bash
 make docker-up
```


## 📦 Optional: Clean the Environment

```bash
make clean
rm -rf frontend/node_modules frontend/dist
```

---

## 🧪 Test the Stack

1. Open [http://localhost:5173](http://localhost:5173)
2. Enter a ticker like `AAPL`
3. Click "Predict"
4. See a table of predicted future prices for:
   - 1 day, 2 days, 1 week, 10 days, 1 month