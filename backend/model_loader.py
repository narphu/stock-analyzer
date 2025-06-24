import os
import boto3
import joblib
import json
import tempfile
from functools import lru_cache
from typing import Optional
import pandas as pd
import yfinance as yf
import tensorflow as tf  # Only required if using LSTM

USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
S3_BUCKET = "shrubb-ai-ml-models"
S3_PREFIX = "models"
S3_CACHE_DIR = "/tmp/shrubb_models"
os.makedirs(S3_CACHE_DIR, exist_ok=True)

s3 = boto3.client("s3")

# === Model path utils ===

def get_model_filename(ticker: str, model: str) -> str:
    return f"{ticker.upper()}.pkl" if model != "lstm" else f"{ticker.upper()}.h5"

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
    acc_path = os.path.join(LOCAL_MODEL_DIR if USE_LOCAL else S3_CACHE_DIR, model, "accuracy.json")

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

def prepare_yfinance_data(ticker: str, period: str = "3y", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    df = df[["Close"]].dropna()
    df["ds"] = df.index
    df = df[["ds", "Close"]].rename(columns={"Close": "y"})
    return df
