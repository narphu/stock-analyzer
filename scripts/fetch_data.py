import yfinance as yf
import pandas as pd

def fetch_data(ticker: str, start_date: str, end_date: str, output_path: str):
    df = yf.download(ticker, start=start_date, end=end_date)
    # Flatten columns manually if ticker name is injected
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)
    df['Ticker'] = ticker
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    fetch_data("AAPL", "2020-01-01", "2020-12-31", "stock_data.csv")