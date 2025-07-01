from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import traceback
import logging
from datetime import datetime
from functools import lru_cache

import pandas as pd
import numpy as np
import yfinance as yf

from model_loader import (
    predict_price,
    get_accuracy_for_ticker,
    prepare_yfinance_data,
    list_available_tickers,
    load_cached_explore_data
)
from data import SP500_TICKERS, SP500_METADATA

# Logger setup
logger = logging.getLogger("uvicorn.error")

# FastAPI initialization with Swagger & ReDoc
app = FastAPI(
    title="Shrubb.ai Stock-Analyzer API",
    version="1.0.0",
    description="Endpoints for predictions, explore (gainers/losers), compare models, and metrics.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stock-analyzer.shrubb.ai",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model options
MODEL_OPTIONS = ["prophet", "arima", "xgboost", "lstm"]

class PredictRequest(BaseModel):
    ticker: str
    model: Optional[str] = "prophet"

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Predict endpoint using unified predict_price
@app.post("/predict")
def predict(req: PredictRequest):
    ticker = req.ticker.upper()
    model_name = req.model.lower()

    if model_name not in MODEL_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported model '{model_name}'")

    # Prepare data to ensure availability
    df = prepare_yfinance_data(ticker)
    if df.empty:
        raise HTTPException(status_code=404, detail="No stock data available")

    today = pd.Timestamp.now().normalize()
    desired_days = [1, 2, 7, 10, 30]

    try:
        predictions = []
        for d in desired_days:
            price = predict_price(ticker, model_name, d)
            predictions.append({
                "days": d,
                "date": (today + pd.Timedelta(days=d)).strftime("%Y-%m-%d"),
                "price": round(price, 2),
            })

        accuracy = get_accuracy_for_ticker(ticker, model_name) or 0.0

        return {
            "ticker": ticker,
            "model": model_name,
            "accuracy": round(accuracy, 4),
            "predictions": predictions,
        }

    except Exception as e:
        logger.error(f"[predict-error] ticker={ticker} model={model_name} err={e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Stock metrics (unchanged)
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

# Explore
@app.get("/explore/top-gainers", response_model=List[Dict])
async def top_gainers(limit: int = Query(10, ge=1, le=100)):
    data = load_cached_explore_data()
    print(data)
    return data.get("top_gainers", [])[:limit]

@app.get("/explore/top-losers", response_model=List[Dict])
async def top_losers(limit: int = Query(10, ge=1, le=100)):
    data = load_cached_explore_data()
    return data.get("top_losers", [])[:limit]

# Compare models DRY
@app.get("/compare/{ticker}", response_model=Dict[str, Dict])
async def compare_models(
    ticker: str,
    days: int = Query(1, ge=1),
):
    t = ticker.upper()
    if t not in SP500_TICKERS:
        raise HTTPException(status_code=404, detail="Ticker not in S&P 500")

    results: Dict[str, Dict] = {}
    for m in MODEL_OPTIONS:
        try:
            pred = predict_price(t, m, days)
            acc = get_accuracy_for_ticker(t, m) or 0.0
            results[m] = {
                "next_prediction": round(pred, 2),
                "accuracy": round(acc, 4),
            }
        except Exception as e:
            results[m] = {"error": str(e)}
    return results
