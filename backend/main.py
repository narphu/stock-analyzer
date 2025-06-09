from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import os
from prophet import Prophet
from datetime import datetime


app = FastAPI()

# Allow frontend access (adjust for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")

class TickerInput(BaseModel):
    ticker: str

def load_model(ticker: str) -> Prophet:
    path = os.path.join(MODEL_DIR, f"{ticker.upper()}_prophet.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Model not available.")
    return joblib.load(path)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(input: TickerInput):
    ticker = input.ticker.upper()
    model = load_model(ticker)

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
        "ticker": ticker,
        "predictions": [
            {
                "days": int(row.days_ahead),
                "date": row.ds.strftime("%Y-%m-%d"),
                "price": round(row.yhat, 2)
            }
            for row in result.itertuples()
        ]
    }
