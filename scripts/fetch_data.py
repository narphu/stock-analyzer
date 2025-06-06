import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", end="2024-12-31")
df.to_csv("data.csv")