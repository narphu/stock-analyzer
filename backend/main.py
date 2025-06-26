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
from model_loader import load_model, get_accuracy_for_ticker, prepare_yfinance_data
import traceback
from typing import Optional
import yfinance as yf
from fastapi import Query
from sklearn.preprocessing import MinMaxScaler
import numpy as np


app = FastAPI()  

# Allow frontend access (adjust for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://stock-analyzer.shrubb.ai","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
MODEL_DIR = os.path.join(BASE_DIR, "ml/models")

class PredictRequest(BaseModel):
    ticker: str
    model: Optional[str] = "prophet"  # default to prophet


@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.url}")
    response = await call_next(request)
    return response

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        model_name = req.model.lower()
        ticker = req.ticker.upper()

        # Load model
        try:
            model = load_model(ticker, model_name)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Model not found")

        # Load data
        df = prepare_yfinance_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="No stock data available")

        today = pd.Timestamp.now().normalize()
        desired_days = [1, 2, 7, 10, 30]

        if model_name == "prophet":
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            forecast = forecast[forecast["ds"] >= today].copy()
            forecast["days_ahead"] = (forecast["ds"] - today).dt.days
            result = forecast[forecast["days_ahead"].isin(desired_days)]

            predictions = [
                {
                    "days": int(row.days_ahead),
                    "date": row.ds.strftime("%Y-%m-%d"),
                    "price": round(row.yhat, 2)
                }
                for row in result.itertuples()
            ]

        elif model_name == "arima":
            y = df["y"].values
            forecast = model.forecast(steps=30)
            predictions = [
                {
                    "days": d,
                    "date": (today + pd.Timedelta(days=d)).strftime("%Y-%m-%d"),
                    "price": round(forecast.iloc[d - 1], 2)
                }
                for d in desired_days if d <= len(forecast)
            ]

        elif model_name == "xgboost":
            df["timestamp"] = df["ds"].astype("int64") // 1e9
            last_ts = df["timestamp"].max()
            step = 86400  # seconds in a day
            predictions = []
            for d in desired_days:
                future_ts = last_ts + d * step
                pred_price = model.predict(np.array([[future_ts]]))[0]
                predictions.append({
                    "days": d,
                    "date": (today + pd.Timedelta(days=d)).strftime("%Y-%m-%d"),
                    "price": round(float(pred_price), 2)

                })

        elif model_name == "lstm":
            window = 10
            scaler = MinMaxScaler()
            scaled = scaler.fit_transform(df[["y"]])
            sequence = scaled[-window:].reshape(1, window, 1)
            predictions = []
            for d in range(1, 31):
                pred = model.predict(sequence, verbose=0)[0][0]
                predictions.append(pred)
                sequence = np.roll(sequence, -1)
                sequence[0, -1, 0] = pred
            predictions = [
                {
                    "days": d,
                    "date": (today + pd.Timedelta(days=d)).strftime("%Y-%m-%d"),
                    "price": round(scaler.inverse_transform([[p]])[0][0], 2)
                }
                for d, p in enumerate(predictions, start=1)
                if d in desired_days
            ]

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model '{model_name}'")

        accuracy = get_accuracy_for_ticker(ticker, model_name)

        return {
            "ticker": ticker,
            "model": model_name,
            "accuracy": accuracy,
            "predictions": predictions
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@lru_cache(maxsize=200)
def fetch_stock_metrics(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "ticker": ticker,
        "name": info.get("longName"),
        "price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "volume": info.get("volume"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "52_week_high": info.get("fiftyTwoWeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow"),
    }

@app.get("/metrics")
def get_stock_metrics(ticker: str = Query(..., description="Stock ticker symbol")):
    try:
        return fetch_stock_metrics(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
