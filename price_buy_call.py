import math
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
import matplotlib.pyplot as plt
import random
import copy

# tickers = input("Enter the stocks you want to analyze (e.g. MRVL, NVDA, ticker): ").split(",")

# historical volatility
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

# rows = []
# for t in tickers:
#     vol, last_close = get_vol_close(t)
#     print(f"ticker: {t}, S0:{round(last_close, 2)}, vol:{round(vol, 3)}")

# Black-Scholes Formula

# normal cdf
def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

# calculating the option price (c)s
def calc_op(x0, K, a, sigma, T):
    """
    Black–Scholes European call price using our formula
    c = x0*Phi(sigma*sqrt(T)+b) - K*exp(-aT)*Phi(b)
    a = 0.04 (4%)
    b = (ln(x0/K)+((a-0.5*vol^2)T)/(sigma*sqrt(T))

    """
    b = (math.log(x0/K) + (a- 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    c = x0 * norm_cdf(sigma*math.sqrt(T)+b)-(K*math.exp(-a*T)*norm_cdf(b))
    
    return c

def calc_iv_backwards(x0, K, a, T, last_price):
    low_iv = 0.0001
    high_iv = 10.0  # Up to 1000% IV, which is very high but can happen in extreme cases
    precision = 0.0001
    
    # Bisection method to calculate IV that matches the last_price
    for _ in range(100):
        mid_iv = (low_iv + high_iv) / 2
        price = calc_op(x0, K, a, mid_iv, T) # calculate the option price using the mid_iv
        
        # its close enough to the last_price, return mid_iv as the IV
        if abs(price - last_price) < precision:
            return mid_iv
        
        # if the calculated price is higher than the last_price, lower IV, else raise IV
        if price > last_price:
            high_iv = mid_iv
        else:
            low_iv = mid_iv
            
    return mid_iv

# Example:
# PLTR 145C Expiring July 17, 2026
currentTime = int(datetime.datetime.now().strftime("%j"))
expireTime = int(datetime.datetime(2026, 7, 17).strftime("%j"))
# for t in tickers:
ticker = get_vol_close("PLTR")
# print(ticker, "ticker")
tickerOption = yf.Ticker("PLTR")
target_date = "2026-07-17"
call_price = 0
try:
    opt_chain = tickerOption.option_chain(target_date)
    calls = opt_chain.calls
    specific_call = calls[calls['strike'] == 145.0]
    print(specific_call)
    yfIV = float(specific_call['impliedVolatility'].iloc[0])
    print("IV:", yfIV)
    if not specific_call.empty:
        # Get the Ask price (what you pay to buy)
        ask_price = specific_call['ask'].values[0]
        bid_price = specific_call['bid'].values[0]
        call_price = (ask_price + bid_price) / 2
        print(f"PLTR $145 Call for {target_date}:")
        print(f"  - Mid: ${call_price}")
    else:
        print(f"The $145 strike is not available for {target_date}.")
    if yfIV < 0.0001:
        print("yfinance's IV is too low, most likely because the market is closed. Will calculate IV using the last option price and the black-scholes formula.")
        call_price = specific_call['lastPrice'].values[0]
        yfIV = calc_iv_backwards(ticker[1], 145, 0.04, (expireTime-currentTime)/365, call_price)
        print("Calculated IV:", yfIV)
except ValueError:
    print(f"Error: {target_date} is not a valid expiration date for PLTR.")
    print(f"Available dates are: {tickerOption.options}")

options_data = [
        {"ticker": "PLTR", 
        "T": (expireTime-currentTime)/365, 
        "K": 145, 
        "mp": call_price, 
        "vol": yfIV,
        "x0": ticker[1]}
    ]

colorArray = ["blue", "green", "orange", "brown", "black"]

plt.figure(figsize=(8,6))
plt.grid(True)
plt.xlabel("Days Passed")
plt.ylabel("Option Price")
plt.title("Predicting PLTR $145 Call Price Expiring 7/17/26")

# random option price changes over time, which will be replaced with brownian motion later.
def random_price_movement(daysLeft, options_data):
    options_data[0]["T"] = daysLeft/365
    # Random Number Generator that will determine the price change for the day:
    # 0: no change, 
    # 1: up a little bit, 
    # 2: up a good amount, 
    # 3: up a lot higher than usual (e.g. earnings beat),
    # 4: down a little bit, 
    # 5: down a good amount,
    # 6: down a lot lower than usual (e.g. earnings miss),
    random_day = random.randint(0,6)
    current_x0 = options_data[0]["x0"]
    current_vol = options_data[0]["vol"]
    if 0 < random_day < 4: # UP
        price_change = current_vol * 0.5 * random_day
        sensitivity = 0.3 # Market is calm when going up
    elif random_day > 3: # DOWN
        price_change = current_vol * -0.5 * (random_day - 3)
        sensitivity = 0.7 # Market is panicky when going down
    else:
        price_change = 0
        sensitivity = 0.1
            
    # update price
    headline_move = 0
    if random.random() < 0.02: 
        # Rare event: Tariff (-8%) or AI Hype (+8%)
        headline_move = options_data[0]["x0"] * random.choice([-0.08, 0.08])
    # 0.04/252 = e.g. 4% annual drift converted to daily
    options_data[0]["x0"] += (0.04/252) + price_change + headline_move
            
    # update volatility using percent change
    pct_move = price_change / current_x0
    options_data[0]["vol"] -= (pct_move * sensitivity)
    # small nudge so iv doesn't go to zero or infinity 
    # (drifts back toward starting sigma by 2% each day)
    options_data[0]["vol"] += (yfIV - options_data[0]["vol"]) * 0.02
            
    # make sure the values are in bounds
    options_data[0]["x0"] = max(0.01, options_data[0]["x0"]) # Price > 0
    options_data[0]["vol"] = max(0.01, options_data[0]["vol"]) # Vol > 0

def inc_currentTime(currentTime, expireTime):
    currentTime = currentTime + 1
    if currentTime == expireTime: 
        currentTime = currentTime - 0.0000000001
    return currentTime

for i in range(0, len(colorArray)):
    timeArray = []
    opArray = []
    copy_options_data = copy.deepcopy(options_data)
    while currentTime <= expireTime:
        random_price_movement(expireTime-currentTime, copy_options_data)
        T_safe = max(0.0001, copy_options_data[0]["T"])
        timeArray.append(currentTime)
        
        #calculate the option using the Black-Scholes formula with the updated price and volatility
        option_p = calc_op(float(copy_options_data[0]["x0"]),
                                    float(copy_options_data[0]["K"]),
                                    0.04,
                                    float(copy_options_data[0]["vol"]),
                                    T_safe)
        opArray.append(option_p)
        currentTime = inc_currentTime(currentTime, expireTime)
        if currentTime > expireTime:
            print("Line: " + str(colorArray[i]) + "\nEnd Price: " + str(copy_options_data[0]["x0"]) + "\n" + "End Option Price: " + str(round(option_p,2)))
        
    plt.plot(timeArray, opArray, marker="o", linestyle='-', color=colorArray[i])
    if i == len(colorArray) - 1:
        plt.show()
    else:
        currentTime = int(datetime.datetime.now().strftime("%j"))
        options_data = [
            {"ticker": "PLTR", 
            "T": (expireTime-currentTime)/365, 
            "K": 145, 
            "mp": call_price, 
            "vol": yfIV,
            "x0": ticker[1]}
        ]

currentTime = int(datetime.datetime.now().strftime("%j"))
options_data = [
    {"ticker": "PLTR", 
    "T": (expireTime-currentTime)/365, 
    "K": 145, 
    "mp": call_price, 
    "vol": yfIV,
    "x0": ticker[1]}
    ]
    
def simulate_option_price(bound, currentTime=currentTime, expireTime=expireTime, options_data=options_data):
    averagePrice = 0
    averageOption = 0
    times0 = 0
    for i in range(0, bound):
        # timeArray = []
        # opArray = []
        while currentTime <= expireTime:
            random_price_movement(expireTime-currentTime, options_data)
            T_safe = max(0.0001, options_data[0]["T"])
            
            # calculate the option
            option_p = calc_op(float(options_data[0]["x0"]),
                                        float(options_data[0]["K"]),
                                        0.04,
                                        float(options_data[0]["vol"]),
                                        T_safe)
            currentTime = inc_currentTime(currentTime, expireTime)
            if currentTime > expireTime:
                averagePrice += options_data[0]["x0"]
                averageOption += option_p
                if averageOption <= 0:
                    times0 += 1

        currentTime = int(datetime.datetime.now().strftime("%j"))
        options_data = [
            {"ticker": "PLTR", 
            "T": (expireTime-currentTime)/365, 
            "K": 145, 
            "mp": call_price, 
            "vol": yfIV,
            "x0": ticker[1]}
        ]    

    averagePrice = round(averagePrice / bound, 2)
    averageOption = round(averageOption / bound, 2)
    print("# of Times Ran:", bound)
    print("Average Price:", averagePrice)
    print("Average Call Price:", averageOption)
    print(f"Number of times reached 0: {times0}")

for i in range(10, 10001, i=i*10):
    simulate_option_price(i, currentTime, expireTime, options_data)