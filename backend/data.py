# backend/data.py
import os
import pandas as pd

# Loads from a local CSV (no network).
# Expected columns: Symbol,Security,GICS Sector,GICS Sub-Industry
# File location defaults to backend/sp500.csv next to this file.
# You can override with SP500_TICKERS_FILE=/absolute/or/relative/path.csv

def _load_sp500():
    base_dir = os.path.dirname(__file__)
    default_path = os.path.join(base_dir, "sp500.csv")
    csv_path = os.getenv("SP500_TICKERS_FILE", default_path)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"S&P 500 CSV not found at {csv_path}. "
            f"Place sp500.csv in {base_dir} or set SP500_TICKERS_FILE."
        )

    # Read CSV and enforce expected columns
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    expected = ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}. Found: {list(df.columns)}")

    # Clean up and de-duplicate
    df["Symbol"] = df["Symbol"].astype(str).str.strip()
    df["Security"] = df["Security"].astype(str).str.strip()
    df["GICS Sector"] = df["GICS Sector"].astype(str).str.strip()
    df["GICS Sub-Industry"] = df["GICS Sub-Industry"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["Symbol"]).reset_index(drop=True)

    # Export structures in the exact shape main.py expects
    tickers = df["Symbol"].tolist()  # keep dots as-is (e.g., BRK.B)
    metadata = {
        row["Symbol"]: {
            "company": row["Security"],
            "sector": row["GICS Sector"],
            "sub_industry": row["GICS Sub-Industry"],
        }
        for _, row in df.iterrows()
    }
    return tickers, metadata

# Exported variables (kept for compatibility with your current main.py)
SP500_TICKERS, SP500_METADATA = _load_sp500()
