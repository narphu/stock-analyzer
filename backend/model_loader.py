import os
import boto3
import joblib
import json
import tempfile
from functools import lru_cache
from typing import Optional, List, Dict
import pandas as pd
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf  # Only required if using LSTM

# Config
USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "../ml/models")
S3_BUCKET = "shrubb-ai-ml-models"
S3_PREFIX = "models"
S3_CACHE_DIR = "/tmp/shrubb_models"
EXPLORE_KEY="analytics/gainers_losers.json"
os.makedirs(S3_CACHE_DIR, exist_ok=True)

s3 = boto3.client("s3")

# === Model path utils ===

def get_model_filename(ticker: str, model: str) -> str:
    ticker = ticker.upper()
    if model == "lstm":
        return f"{ticker}.keras"
    elif model in {"prophet", "arima", "xgboost"}:
        return f"{ticker}.pkl"
    else:
        raise ValueError(f"Unsupported model type: {model}")


def get_local_model_path(ticker: str, model: str) -> str:
    return os.path.join(LOCAL_MODEL_DIR, model, get_model_filename(ticker, model))


def get_cached_s3_model_path(ticker: str, model: str) -> str:
    return os.path.join(S3_CACHE_DIR, model, get_model_filename(ticker, model))

# === Download logic ===

@lru_cache(maxsize=256)
def download_model_from_s3(ticker: str, model: str = "prophet") -> str:
    ticker = ticker.upper()
    filename = get_model_filename(ticker, model)
    local_path = get_cached_s3_model_path(ticker, model)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if os.path.exists(local_path):
        return local_path

    s3_key = f"{S3_PREFIX}/{model}/{filename}"
    print(f"⬇️ Downloading s3://{S3_BUCKET}/{s3_key}")
    s3.download_file(S3_BUCKET, s3_key, local_path)

    return local_path

# === Model loading ===

@lru_cache(maxsize=256)
def load_model(ticker: str, model: str = "prophet"):
    ticker = ticker.upper()
    path = (
        get_local_model_path(ticker, model)
        if USE_LOCAL else
        download_model_from_s3(ticker, model)
    )
    print(f"📂 Loading model from: {path}")
    return tf.keras.models.load_model(path) if model == "lstm" else joblib.load(path)

# === Accuracy lookup ===

def get_accuracy_for_ticker(ticker: str, model: str = "prophet") -> Optional[float]:
    ticker = ticker.upper()
    acc_path = os.path.join(
        LOCAL_MODEL_DIR if USE_LOCAL else S3_CACHE_DIR,
        model,
        "accuracy.json"
    )

    if not os.path.exists(acc_path):
        if not USE_LOCAL:
            try:
                os.makedirs(os.path.dirname(acc_path), exist_ok=True)
                s3_key = f"{S3_PREFIX}/{model}/accuracy.json"
                print(f"⬇️ Downloading accuracy file: s3://{S3_BUCKET}/{s3_key}")
                s3.download_file(S3_BUCKET, s3_key, acc_path)
            except Exception:
                return None
        else:
            return None

    try:
        with open(acc_path) as f:
            data = json.load(f)
            return round(data.get(ticker, 0.0), 4)
    except Exception:
        return None

# === Data prep ===

def prepare_yfinance_data(ticker: str, period: str = "3y", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    df = df[["Close"]].dropna()
    df["ds"] = df.index
    return df[["ds", "Close"]].rename(columns={"Close": "y"})

# === Unified prediction interface ===

def predict_price(ticker: str, model: str, days: int) -> float:
    """
    Predict price for `ticker` using `model` over `days` horizon.
    Returns a single float.
    """
    ticker = ticker.upper()
    mdl = load_model(ticker, model)

    df = prepare_yfinance_data(ticker)
    today = pd.Timestamp.now().normalize()

    if model == "prophet":
        future = mdl.make_future_dataframe(periods=days)
        forecast = mdl.predict(future)
        future_rows = forecast[forecast["ds"] >= today]
        target_index = min(days - 1, len(future_rows) - 1)
        row = future_rows.iloc[target_index]
        return float(row.yhat)

    if model == "arima":
        fc = mdl.forecast(steps=days)
        return float(fc.iloc[days - 1])

    if model == "xgboost":
        df_ts = df.copy()
        df_ts["timestamp"] = df_ts["ds"].astype("int64") // 10**9
        last_ts = df_ts["timestamp"].max()
        future_ts = np.array([[last_ts + days * 86400]])
        return float(mdl.predict(future_ts)[0])

    if model == "lstm":
        window = 10
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df[["y"]])
        seq = scaled[-window:].reshape(1, window, 1)
        for _ in range(days):
            p = mdl.predict(seq, verbose=0)[0][0]
            seq = np.roll(seq, -1)
            seq[0, -1, 0] = p
        return float(scaler.inverse_transform([[p]])[0][0])

    raise ValueError(f"Unsupported model {model}")
# === List available tickers ===

@lru_cache(maxsize=8)
def list_available_tickers(model: str = "prophet") -> List[str]:
    """
    Returns tickers with model files, from LOCAL_MODEL_DIR or S3 under S3_PREFIX/model/.
    """
    model = model.lower()
    ext = ".keras" if model == "lstm" else ".pkl"

    if USE_LOCAL:
        dirpath = os.path.join(LOCAL_MODEL_DIR, model)
        try:
            return [os.path.splitext(f)[0] for f in os.listdir(dirpath) if f.endswith(ext)]
        except FileNotFoundError:
            return []

    # S3 fallback
    prefix = f"{S3_PREFIX}/{model}/"
    tickers = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            name = os.path.basename(obj["Key"])
            if name.endswith(ext):
                tickers.append(os.path.splitext(name)[0])
    return tickers

# Explore data precomputed. Only available on S3.
def load_cached_explore_data():
    try:
        if USE_LOCAL:
            explore_data_path = os.path.join(LOCAL_MODEL_DIR,EXPLORE_KEY)
            print(f"Reading explore data from {explore_data_path}")
            with open(explore_data_path, 'r') as f:
                content = json.load(f)
        else:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=EXPLORE_KEY)
            content = json.loads(obj["Body"].read().decode("utf-8"))
        return content
    except Exception as e:
        print(f"⚠️ Failed to load cached explore data: {e}")
        return {"gainers": [], "losers": []}
