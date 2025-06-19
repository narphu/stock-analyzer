import os
import joblib
import yfinance as yf
import pandas as pd
from prophet import Prophet
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from functools import lru_cache    # ⚡ Simple in-memory caching

USE_LOCAL = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
if USE_LOCAL:
    # Use ./backend/models relative to project root
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    MODEL_DIR = os.getenv("MODEL_OUTPUT_DIR", os.path.join(BASE_DIR, "backend", "models"))
else:
    # SageMaker expects model artifacts here
    MODEL_DIR = "/opt/ml/model"
os.makedirs(MODEL_DIR, exist_ok=True)


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    tickers = pd.read_html(str(table))[0]["Symbol"].tolist()
    tickers = [t.replace(".", "-") for t in tickers]  # BRK.B → BRK-B
    return tickers

def train(ticker):
    try:
        model_path = os.path.join(MODEL_DIR, f"{ticker}_prophet.pkl")
        if os.path.exists(model_path):
            print(f"⏭️ Skipping {ticker}: model already exists")
            return

        print(f"🔄 Training {ticker}")
        df = prepare_yfinance_data(ticker)
        if df.empty:
            print(f"❌ No usable data for {ticker}")
            return

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        joblib.dump(model, model_path)
        print(f"✅ Saved: {model_path}")
    except Exception as e:
        print(f"❌ Error training {ticker}: {e}")

def train_all_sp500():
    tickers = get_sp500_tickers()
    print(f"📈 Found {len(tickers)} S&P 500 tickers")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(train, tickers)


def prepare_yfinance_data(ticker: str, period: str = "3y", interval: str = "1d") -> pd.DataFrame:
    """
    Download and clean historical stock data for Prophet training.
    Ensures a flat column format with 'ds' and 'y'.
    """
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    df = df[["Close"]].dropna()
    df["ds"] = df.index
    df = df[["ds", "Close"]].rename(columns={"Close": "y"})

    print("✅ Last available date for", ticker, "is", df["ds"].max())

    return df

if __name__ == "__main__":
    train_all_sp500()
