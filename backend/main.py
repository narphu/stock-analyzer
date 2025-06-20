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
from model_loader import load_model
import traceback
import yfinance as yf
from fastapi import Query


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

    
