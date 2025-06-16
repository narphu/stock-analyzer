from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import os
from prophet import Prophet
from datetime import datetime
from functools import lru_cache    # ⚡ Simple in-memory caching


app = FastAPI(root_path="/api")  

# Allow frontend access (adjust for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")

class PredictRequest(BaseModel):
    ticker: str

@lru_cache(maxsize=100)
def load_model(ticker: str):
    path = os.path.join(MODEL_DIR, f"{ticker}_prophet.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model for {ticker} not found")
    return joblib.load(path)

def load_model(ticker: str) -> Prophet:
    path = os.path.join(MODEL_DIR, f"{ticker.upper()}_prophet.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Model not available.")
    return joblib.load(path)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):

    try:
        model = load_model(req.ticker.upper())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    today = pd.Timestamp.now().normalize()

    # Generate forecast
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # Only keep future rows
    forecast = forecast[forecast["ds"] >= today].copy()
    forecast["days_ahead"] = (forecast["ds"] - today).dt.days

    # Return selected future horizons
    desired_days = [1, 2, 7, 10, 30]
    result = forecast[forecast["days_ahead"].isin(desired_days)]

    return {
        "ticker":  req.ticker.upper(),
        "predictions": [
            {
                "days": int(row.days_ahead),
                "date": row.ds.strftime("%Y-%m-%d"),
                "price": round(row.yhat, 2)
            }
            for row in result.itertuples()
        ]
    }
