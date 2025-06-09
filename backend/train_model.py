from prophet import Prophet
import yfinance as yf
import pandas as pd
import joblib
import os

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def train(ticker):
    print(f"🔄 Training model for {ticker}")

    df = prepare_yfinance_data(ticker)

    if df.empty:
        print(f"❌ Invalid data for {ticker}")
        return

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    path = os.path.join(MODEL_DIR, f"{ticker}_prophet.pkl")
    joblib.dump(model, path)
    print(f"✅ Model saved: {path}")

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
    for ticker in TICKERS:
        train(ticker)
