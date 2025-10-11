import os
import joblib
import yfinance as yf
import pandas as pd
from prophet import Prophet
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from functools import lru_cache

from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error
from collections import defaultdict
import json
import numpy as np
import warnings
import gc


warnings.filterwarnings("ignore")

USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
if USE_LOCAL:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
    MODEL_DIR = os.getenv("MODEL_OUTPUT_DIR", os.path.join(BASE_DIR, "models"))
else:
    MODEL_DIR = "/opt/ml/model"

os.makedirs(MODEL_DIR, exist_ok=True)

# Dictionary to track accuracy scores
accuracy_tracker = defaultdict(dict)

def get_sp500_tickers():
    # Optional local fallback (set SP500_TICKERS_FILE to a csv/json path with column/key 'Symbol')
    local_file = os.getenv("SP500_TICKERS_FILE")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }

    # 1) Try live fetch with a real UA
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        # Try the table by id first
        tables = pd.read_html(resp.text, attrs={"id": "constituents"}, flavor="lxml")
        if not tables:
            # Fallback: scan all tables and pick the one that has a 'Symbol' column
            all_tables = pd.read_html(resp.text, flavor="lxml")
            tables = [t for t in all_tables if "Symbol" in t.columns]

        if tables:
            df = tables[0]
            tickers = (
                df["Symbol"]
                .astype(str)
                .str.strip()
                .str.replace(".", "-", regex=False)  # BRK.B -> BRK-B
                .tolist()
            )
            if tickers:
                return tickers
        # If we got here, live parse failed
        raise RuntimeError("Wikipedia structure changed or empty table.")
    except Exception as e:
        # 2) Fallback: local file if provided
        if local_file and os.path.exists(local_file):
            ext = os.path.splitext(local_file)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(local_file)
                if "Symbol" in df.columns:
                    return (df["Symbol"].astype(str).str.replace(".", "-", regex=False)).tolist()
            elif ext in (".json", ".ndjson"):
                with open(local_file, "r") as f:
                    data = json.load(f)
                # Accept either a dict with "Symbol" or a list of dicts
                if isinstance(data, dict) and "Symbol" in data:
                    data = [data]
                if isinstance(data, list) and data and "Symbol" in data[0]:
                    return [str(d["Symbol"]).replace(".", "-") for d in data]

        # 3) Last resort: tiny baked-in seed list to keep the pipeline alive
        seed = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "BRK-B", "JPM", "XOM", "UNH"]
        print(f"⚠️ get_sp500_tickers fallback due to: {e}. Using a seed list of {len(seed)} tickers.")
        return seed

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

def save_model(model, path, is_keras=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if is_keras:
        model.save(path.replace(".h5", ".keras")) 
    else:
        joblib.dump(model, path)

def train_prophet(ticker, df):
    path = os.path.join(MODEL_DIR, "prophet", f"{ticker}.pkl")
    if os.path.exists(path):
        print(f"⏭️ Prophet: {ticker} already trained.")
        return
    model = Prophet(daily_seasonality=True)
    model.fit(df)
    forecast = model.predict(df)
    acc = 1 - mean_absolute_percentage_error(df["y"], forecast["yhat"])
    save_model(model, path)
    accuracy_tracker["prophet"][ticker] = round(acc, 4)
    print(f"✅ Prophet Model for {ticker} trained.")


def train_arima(ticker, df):
    path = os.path.join(MODEL_DIR, "arima", f"{ticker}.pkl")
    if os.path.exists(path) or len(df) < 100:
        return
    model = ARIMA(df["y"], order=(5, 1, 0)).fit()
    forecast = model.predict(start=0, end=len(df)-1)
    acc = 1 - mean_absolute_percentage_error(df["y"], forecast)
    save_model(model, path)
    accuracy_tracker["arima"][ticker] = round(acc, 4)
    print(f"✅ ARIMA Model for {ticker} trained.")

def train_xgboost(ticker, df):
    path = os.path.join(MODEL_DIR, "xgboost", f"{ticker}.pkl")
    if os.path.exists(path) or len(df) < 100:
        return
    df["timestamp"] = df["ds"].astype("int64") // 1e9
    X = df["timestamp"].values.reshape(-1, 1)
    y = df["y"].values
    model = XGBRegressor(n_estimators=100)
    model.fit(X, y)
    preds = model.predict(X)
    acc = 1 - mean_absolute_percentage_error(y, preds)
    save_model(model, path)
    accuracy_tracker["xgboost"][ticker] = round(acc, 4)
    print(f"✅ XGBoost Model for {ticker} trained.")

#  Handles division-by-zero gracefully.
def safe_mape(y_true, y_pred):
    mask = y_true != 0
    if not np.any(mask):
        return float('inf')
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask]))

def train_lstm(ticker, df):
    path = os.path.join(MODEL_DIR, "lstm", f"{ticker}.keras")
    if os.path.exists(path) or len(df) < 100:
        return

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["y"]])
    X, y = [], []
    window = 10
    for i in range(window, len(scaled)):
        X.append(scaled[i - window:i, 0])
        y.append(scaled[i, 0])
    X = np.array(X).reshape(-1, window, 1)
    y = np.array(y)

    # Split into train/val for better generalization
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    model = Sequential()
    model.add(LSTM(50, activation="relu", input_shape=(window, 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")

    model.fit(
        X_train, y_train,
        epochs=20,
        verbose=0,
        validation_data=(X_val, y_val),
        callbacks=[EarlyStopping(patience=3, monitor="val_loss")]
    )

    preds = model.predict(X_val).flatten()
    acc = 1 - safe_mape(y_val, preds)
    save_model(model, path, is_keras=True)
    accuracy_tracker["lstm"][ticker] = round(acc, 4)
    print(f"✅ LSTM Model for {ticker} trained.")

# We split the model training into light and heavy models to optimize CPU usage when using smaller instancess
# as ml.m5large
def train_light_models(ticker):
    try:
        print(f"🔄 Training models for {ticker}")
        df = prepare_yfinance_data(ticker)
        if df.empty:
            print(f"❌ No data for {ticker}")
            return
        train_prophet(ticker, df)
        gc.collect()
        train_arima(ticker, df)
        gc.collect()
        train_xgboost(ticker, df)
        gc.collect()
        print(f"✅ Completed training: {ticker}")
    except Exception as e:
        print(f"❌ Failed {ticker}: {e}")

def train_heavy_models(ticker):
    try:
        print(f"🔄 Training models for {ticker}")
        df = prepare_yfinance_data(ticker)
        if df.empty:
            print(f"❌ No data for {ticker}")
            return
        train_lstm(ticker, df)
        gc.collect()
        print(f"✅ Completed training: {ticker}")
    except Exception as e:
        print(f"❌ Failed {ticker}: {e}")

def train_all_sp500():
    tickers = get_sp500_tickers()
    print(f"📈 Found {len(tickers)} S&P 500 tickers")
    # This maximizes CPU usage while avoiding deadlocks and mutex corruption from TensorFlow under concurrency.
    # Light models (thread-safe)
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(train_light_models, tickers)

    # Heavy models (TensorFlow)
    with ProcessPoolExecutor(max_workers=1) as executor:
        executor.map(train_heavy_models, tickers)
    
    print(f"{accuracy_tracker.items()}")
    
    # Save accuracy.json per model
    for model, accs in accuracy_tracker.items():
        try:
            path = os.path.join(MODEL_DIR, model, "accuracy.json")
            print(f"Accuracy for model: {model} -> {accs}" )
            with open(path, "w") as f:
                json.dump(accs, f, indent=2)
            print(f"📈 Saved accuracy for {model} → {path}")
        except Exception as e:
            print(f"❌ Failed to save accuracy.json: {e}")

if __name__ == "__main__":
    train_all_sp500()