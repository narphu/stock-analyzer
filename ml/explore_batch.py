import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
from tensorflow import keras
import joblib
import os
import boto3
import tempfile
import yfinance as yf
from train_model import get_sp500_tickers
from datetime import datetime
import json

USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
if USE_LOCAL:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    MODEL_DIR = os.getenv("MODEL_OUTPUT_DIR", os.path.join(BASE_DIR, "models"))
else:
    MODEL_DIR = "/opt/ml/model"

LOOKAHEAD_DAYS = 30
TOP_N = 5
MODEL_NAMES = ["prophet", "arima", "xgboost", "lstm"]
BUCKET = "shrubb-ai-ml-models"
DEST_KEY = "analytics/gainers_losers.json"
SP500_TICKERS = get_sp500_tickers()

s3 = boto3.client("s3")

def prepare_yfinance_data(ticker: str):
    df = yf.download(ticker, period="1y", interval="1d")
    df = df.reset_index()[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def download_model(ticker: str, model: str) -> str:
    ext = ".keras" if model == "lstm" else ".pkl"
    key = f"models/{model}/{ticker}{ext}"
    local_path = os.path.join(MODEL_DIR, model, f"{ticker}{ext}")

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if not os.path.exists(local_path):
        print(f"⬇️ Downloading model from s3://{BUCKET}/{key}")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            s3.download_file(BUCKET, key, tmp.name)
            os.rename(tmp.name, local_path)

    return local_path


def load_model(ticker: str, model: str):
    path = download_model(ticker, model)

    if model == "prophet":
        return joblib.load(path)
    elif model == "arima":
        return joblib.load(path)
    elif model == "xgboost":
        return joblib.load(path)
    elif model == "lstm":
        return keras.models.load_model(path, compile=False)
    else:
        raise ValueError(f"Unsupported model {model}")


def predict_price(ticker: str, model: str, days: int) -> float:
    ticker = ticker.upper()
    mdl = load_model(ticker, model)
    df = prepare_yfinance_data(ticker)
    today = pd.Timestamp.now().normalize()

    if model == "prophet":
        future = mdl.make_future_dataframe(periods=days)
        forecast = mdl.predict(future)
        future_rows = forecast[forecast["ds"] >= today]
        target_index = min(days - 1, len(future_rows) - 1)
        return float(future_rows.iloc[target_index]["yhat"])

    elif model == "arima":
        forecast = mdl.forecast(steps=days)
        return float(forecast.iloc[days - 1])

    elif model == "xgboost":
        df_ts = df.copy()
        df_ts["timestamp"] = df_ts["ds"].astype("int64") // 10**9
        last_ts = df_ts["timestamp"].max()
        future_ts = np.array([[last_ts + days * 86400]])
        return float(mdl.predict(future_ts)[0])

    elif model == "lstm":
        window = 10
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df[["y"]])
        seq = scaled[-window:].reshape(1, window, 1)

        for _ in range(days):
            p = mdl.predict(seq, verbose=0)[0][0]
            seq = np.roll(seq, -1)
            seq[0, -1, 0] = p

        return float(scaler.inverse_transform([[p]])[0][0])

    else:
        raise ValueError(f"Unsupported model {model}")
    

def get_current_price(ticker: str) -> float:
    try:
        data = yf.download(ticker, period="7d", interval="1d")
        return data["Close"][ticker][-1] if not data.empty else None
    except Exception as e:
        print(f"⚠️ Failed to get current price for {ticker}: {e}")
        return None


def compute_gainers_losers():
    results = []

    for ticker in SP500_TICKERS:
        try:
            current_price = get_current_price(ticker)
            if not current_price:
                continue

            preds = []
            for model in MODEL_NAMES:
                try:
                    pred = predict_price(ticker, model, LOOKAHEAD_DAYS)
                    preds.append(pred)
                except Exception as e:
                    print(f"⚠️ Model {model} failed for {ticker}: {e}")
                    continue

            if not preds:
                continue

            avg_pred = sum(preds) / len(preds)
            percent_change = ((avg_pred - current_price) / current_price) * 100

            results.append({
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "predicted_price": round(avg_pred, 2),
                "percent_change": round(percent_change, 2),
            })

        except Exception as e:
            print(f"⚠️ Error processing {ticker}: {e}")

    gainers = sorted(results, key=lambda x: x["percent_change"], reverse=True)[:TOP_N]
    losers = sorted(results, key=lambda x: x["percent_change"])[:TOP_N]

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "models_used": MODEL_NAMES,
        "top_gainers": gainers,
        "top_losers": losers,
    }

    if not USE_LOCAL:

        s3.put_object(
            Bucket=BUCKET,
            Key=DEST_KEY,
            Body=json.dumps(output),
            ContentType="application/json"
        )
    else:
        try:
            path = os.path.join(MODEL_DIR, DEST_KEY)
            with open(path, "w") as f:
                json.dump(output, f, indent=2)
            print(f"📈 Saved gainers losers for {output}")
        except Exception as e:
            print(f"❌ Failed to save gainers_losers.json: {e}")

    print(f"✅ Uploaded analytics to s3://{BUCKET}/{DEST_KEY}")


if __name__ == "__main__":
    compute_gainers_losers()