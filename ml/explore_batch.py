import os
import json
import boto3
import joblib
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMAResults
from keras.models import load_model
import numpy as np

MODEL_DIR = "models"
BUCKET = "shrubb-ai-ml-models"
DEST_KEY = "analytics/gainers_losers.json"
S3 = boto3.client("s3")
SUPPORTED_MODELS = ["prophet", "arima", "xgboost", "lstm"]
LOOKAHEAD_DAYS = 30
TOP_N = 5

def compute_volatility(df):
    df["returns"] = df["Close"].pct_change()
    return round(df["returns"].std() * 100, 2)  # percentage


def load_all_models():
    model_cache = {}
    for model in SUPPORTED_MODELS:
        model_cache[model] = {}
        local_dir = os.path.join(MODEL_DIR, model)
        os.makedirs(local_dir, exist_ok=True)
        response = S3.list_objects_v2(Bucket=BUCKET, Prefix=f"models/{model}/")
        for obj in response.get("Contents", []):
            if obj["Key"].endswith((".pkl", ".keras")):
                filename = obj["Key"].split("/")[-1]
                ticker = filename.split(".")[0]
                local_path = os.path.join(local_dir, filename)
                S3.download_file(BUCKET, obj["Key"], local_path)
                if model == "prophet":
                    model_cache[model][ticker] = joblib.load(local_path)
                elif model == "arima":
                    model_cache[model][ticker] = ARIMAResults.load(local_path)
                elif model == "xgboost":
                    import xgboost as xgb
                    model_cache[model][ticker] = xgb.Booster()
                    model_cache[model][ticker].load_model(local_path)
                elif model == "lstm":
                    model_cache[model][ticker] = load_model(local_path)
    return model_cache


def forecast_average_price(ticker, models):
    df = yf.download(ticker, period="6mo", progress=False)
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    df = df[["y"]].reset_index()
    df.rename(columns={"Date": "ds"}, inplace=True)
    today = df.ds.max()
    future_date = today + timedelta(days=LOOKAHEAD_DAYS)
    
    forecasts = []
    for model_name, model in models.items():
        try:
            if model_name == "prophet":
                future = model.make_future_dataframe(periods=LOOKAHEAD_DAYS)
                forecast = model.predict(future)
                pred = forecast[forecast.ds == future_date]["yhat"].values[0]
            elif model_name == "arima":
                pred = model.forecast(LOOKAHEAD_DAYS)[-1]
            elif model_name == "xgboost":
                ts = int(pd.Timestamp(today).timestamp()) + LOOKAHEAD_DAYS * 86400
                dmatrix = xgb.DMatrix(np.array([[ts]]))
                pred = model.predict(dmatrix)[0]
            elif model_name == "lstm":
                from sklearn.preprocessing import MinMaxScaler
                scaled = MinMaxScaler().fit_transform(df[["y"]])
                X = [scaled[-10:].reshape(1, 10, 1)]
                pred = scaled[-1][0] * model.predict(np.array(X)).flatten()[0]  # Reverse scaling dummy
            forecasts.append(float(pred))
        except Exception as e:
            print(f"⚠️ {ticker} {model_name} prediction failed: {e}")
    return np.mean(forecasts) if forecasts else None


def generate_gainers_losers():
    model_cache = load_all_models()
    tickers = set.intersection(*[set(models.keys()) for models in model_cache.values()])
    results = []

    for ticker in tickers:
        models = {m: model_cache[m][ticker] for m in SUPPORTED_MODELS if ticker in model_cache[m]}
        avg_pred_price = forecast_average_price(ticker, models)
        if avg_pred_price is None:
            continue
        current_price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        change = ((avg_pred_price - current_price) / current_price) * 100
        results.append({"ticker": ticker, "change": round(change, 2)})

    results = sorted(results, key=lambda x: x["change"], reverse=True)
    gainers = results[:TOP_N]
    losers = results[-TOP_N:][::-1]

    payload = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "top_gainers": gainers,
        "top_losers": losers,
    }

    with open("gainers_losers.json", "w") as f:
        json.dump(payload, f, indent=2)

    S3.upload_file("gainers_losers.json", BUCKET, DEST_KEY)
    print("✅ gainers_losers.json uploaded to S3")


if __name__ == "__main__":
    generate_gainers_losers()
