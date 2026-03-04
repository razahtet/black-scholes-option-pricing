import yfinance as yf
import numpy as np
import pandas as pd

tickers = ["MRVL", "NVDA", "IONQ", "PLTR"]

def get_vol_close(ticker, period="1y"):
    data = yf.download(ticker, period=period, interval="1d", auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"][ticker].dropna()
    else:
        close = data["Close"].dropna()

    # Daily log returns
    log_returns = np.log(close / close.shift(1)).dropna()

    # Annualized volatility (252 trading days)
    vol = log_returns.std() * np.sqrt(252)

    # market price = last closing price for the 1yr time period
    last_close = close.iloc[-1] # last close

    return [float(vol), float(last_close)]

rows = []
for t in tickers:
    vol, last_close = get_vol_close(t)
    print(f"ticker: {t}, S0:{round(last_close, 2)}, vol:{round(vol, 3)}")
