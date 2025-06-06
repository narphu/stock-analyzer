# Developer Guide: Stock Trend Analyzer

This guide provides step-by-step instructions to run and test the Stock Trend Analyzer project locally using your machine — no Kubernetes or cloud setup needed yet.

---

## ✅ Prerequisites
- Python 3.10+
- Docker
- Node.js & npm (for frontend, optional)
- `pip` for Python packages

---

## 🧪 Step 1: Setup & Train the Model

```bash
python -m venv venv
source venv/bin/activate
pip install pandas scikit-learn yfinance
cd stock-analyzer/scripts
python fetch_data.py
python train_model.py
```

---

## 🚀 Step 2: Run the FastAPI Backend

```bash
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit the API: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔍 Step 3: Test the API

### Health Check

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok"}
```

### Sample Prediction

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"Open": 174.03, "High": 175.0, "Low": 173.5, "Close": 174.6, "Volume": 70000000}'
```

---

## 🐳 Step 4: Run with Docker

### Build the Docker image

```bash
cd stock-analyzer/backend
docker build -t stock-analyzer-backend .
```

### Run the container

```bash
docker run -p 8080:8080 stock-analyzer-backend
```

### Test the running container

```bash
curl http://localhost:8080/health
```