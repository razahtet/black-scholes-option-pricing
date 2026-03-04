# Graph comparing the yfinance IV with the getcloseIV (historical IV) 
#  I calculate by taking the last year of prices of the stock (referencing code from compute_vols.py) 
# and make an analysis on each affects the calculated black-scholes price and the market price.
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from compute_vols import get_vol_close
from price_buy_call import calc_op, get_IV_mp

currentTime = int(datetime.datetime.now().strftime("%j"))
expireTime = int(datetime.datetime(2026, 7, 17).strftime("%j"))
tickerInf = get_vol_close("PLTR")
results = []
iv_and_mp = get_IV_mp("PLTR", "2026-07-17", 145, 0.04, (expireTime-currentTime)/365)
if iv_and_mp != None:
    iv = iv_and_mp[0]
    call_price = iv_and_mp[1]
else:
    iv = 0
    call_price = 0
    print("Please recheck the data.")

options_data = [
        {"ticker": "PLTR", 
        "T": (expireTime-currentTime)/365, 
        "K": 145, 
        "mp": call_price, #market price
        "vol": tickerInf[0], # get_vol_close returns the historical volatility calculated and the last closing stock price
        "x0": tickerInf[1]},
        {"ticker": "PLTR", 
        "T": (expireTime-currentTime)/365, 
        "K": 145, 
        "mp": call_price, #market price
        "vol": iv, # get_vol_close returns the historical volatility calculated and the last closing stock price
        "x0": tickerInf[1]},
    ]

for option in options_data:
    tickerName = option["ticker"]
    T = float(option["T"])
    K = float(option["K"])
    mp = float(option["mp"])

    x0 = float(option["x0"])
    sigma = float(option["vol"])

    option_price = calc_op(x0, K, 0.04, sigma, T)
    diff = option_price - mp

    results.append({
        "ticker": tickerName,
        "T_years": round(T, 4),
        "K": round(K, 2),
        "x0": round(x0, 2),
        "sigma": round(sigma, 3),
        "market_price": round(mp, 4),
        "calc_option_price": round(option_price, 4),
        "model_minus_market": round(diff, 4),
    })

df_res = pd.DataFrame(results)
print("\nThe first table compares the calculated option price with historical volatility and market option price.")
print("\nThe second table compares the calculated option price with implied volatility and market option price.")
print(df_res[["ticker", "T_years", "K", "x0", "sigma",
              "market_price", "calc_option_price", "model_minus_market"]].to_string(index=False))
