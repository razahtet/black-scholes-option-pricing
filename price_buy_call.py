import math
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
import matplotlib.pyplot as plt
import random
import copy
from compute_vols import get_vol_close

# Input the Option you want to analyze (e.g. PLTR 145C Expiring July 17, 2026)
questArray = ["Enter the stock ticker you want to analyze (e.g. PLTR): ",
              "Enter the expiration date (e.g. 2026-07-17): ",
              "Enter the strike price (e.g. 145): "]
optionArray = []
for i in range(0, len(questArray)):
    validInput = False
    questInput = ""
    while not validInput:
        try:
            if i == 0:
                questInput = input(questArray[i])
                ticker_data = yf.Ticker(questInput).history(period="1d") # check if ticker is valid
                if ticker_data.empty:
                    print(f"Error: {questInput} is not a valid stock ticker.")
                    validInput = False
                else:
                    validInput = True
            elif i == 1:
                questInput = input(questArray[i])
                yf.Ticker(optionArray[0]).option_chain(questInput)
                validInput = True
            elif i == 2:
                questInput = float(input(questArray[i]))
                calls = yf.Ticker(optionArray[0]).option_chain(optionArray[1]).calls
                strikes_list = calls['strike'].unique()
                if questInput not in strikes_list:
                    print(f"Error: {questInput} is not a valid strike price.")
                    print(f"Some of the available strike prices for {optionArray[0]} expiring {optionArray[1]} are: {calls['strike'].unique()[:15]}")
                    validInput = False
                else:
                    validInput = True
        except ValueError:
            if i == 1:
                print(f"Error: {questInput} is not a valid expiration date for {optionArray[0]}.")
                print(f"Some available dates are: {yf.Ticker(optionArray[0]).options[:7]}")
            validInput = False
    if validInput:
        optionArray.append(questInput)

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
dateA = optionArray[1].split("-")
expireTime = int(datetime.datetime(int(dateA[0]), int(dateA[1]), int(dateA[2])).strftime("%j"))
# for t in tickers:
tickerInf = get_vol_close(optionArray[0])
target_date = optionArray[1]

def get_IV_mp(ticker, target_date, strike, a, T):
    print("Data pulled from yFinance API")
    try:
        tickerOption = yf.Ticker(ticker)
        opt_chain = tickerOption.option_chain(target_date)
        calls = opt_chain.calls
        specific_call = calls[calls['strike'] == strike]
        yfIV = float(specific_call['impliedVolatility'].iloc[0])
        print(f"IV: {yfIV}")
        if not specific_call.empty:
            # Get the Call price (what you pay to buy)
            ask_price = specific_call['ask'].values[0]
            bid_price = specific_call['bid'].values[0]
            last_price = specific_call['lastPrice'].values[0]
            call_price = (ask_price + bid_price) / 2
            print(f"\n{ticker} ${strike} Call for {target_date}:")
            print(f"Bid: ${bid_price}, Ask: ${ask_price}")
            print(f"Last Price: ${last_price}")
            print(f"Mid Price: ${call_price}")
        else:
            print(f"The ${strike} strike is not available for {target_date}.")
            return None
        if yfIV < 0.0001:
            print("\nyfinance's IV is too low, most likely because the market is closed. Will calculate IV using the last option price and the black-scholes formula.")
            call_price = specific_call['lastPrice'].values[0]
            print(f"Last Stock Price: {tickerInf[1]}")
            yfIV = calc_iv_backwards(tickerInf[1], strike, a, T, call_price)
            print(f"Calculated IV: {yfIV}")
        return [yfIV, call_price]
    except ValueError:
        print(f"Error: {target_date} is not a valid expiration date for {ticker}.")
        print(f"Available dates are: {tickerOption.options}")
        return None

iv_mp = get_IV_mp(optionArray[0], target_date, optionArray[2], 0.04, (expireTime-currentTime)/365)
if iv_mp != None:
    iv = iv_mp[0]
    call_price = iv_mp[1]
else:
    iv = 0
    call_price = 0

options_data = [
        {"ticker": optionArray[0], 
        "T": (expireTime-currentTime)/365, 
        "K": optionArray[2], 
        "mp": call_price, 
        "vol": iv,
        "x0": tickerInf[1]}
    ]

colorArray = ["blue", "green", "orange", "brown", "black", "purple", "cyan"]

plt.figure(figsize=(8,6))
plt.grid(True)
plt.xlabel("Days Passed")
plt.ylabel("Option Price")
plt.title(f"Predicting {optionArray[0]} ${optionArray[2]} Call Price Expiring {optionArray[1]}")

# random option price changes over time, which will be replaced with brownian motion later.
def random_price_movement(daysLeft, options_data):
    options_data[0]["T"] = daysLeft/365
    # Random Number Generator that will determine the price change for the day:
    # 0: no change
    # 1: up a little bit
    # 2: up a good amount
    # 3: up a lot higher than usual (e.g. earnings beat)
    # 4: down a little bit
    # 5: down a good amount
    # 6: down a lot lower than usual (e.g. earnings miss)
    random_day = random.randint(0,6)
    current_x0 = options_data[0]["x0"]
    current_vol = options_data[0]["vol"]
    sensitivity_map = {
        0: 0.1, # No change
        1: 0.3, 4: 0.3, # lower sensitivity for small up or down days
        2: 0.5, 5: 0.5, # middle amount of sensitivity for normal up or down days
        3: 0.7, 6: 0.7 # market will react more strongly to good or bad news (panic), so higher sensitivity
    }
    sensitivity = sensitivity_map[random_day]
    if 0 < random_day < 4: # UP:
        price_change = current_vol * 0.5 * random_day
    elif random_day > 3: # DOWN
        price_change = current_vol * -0.5 * (random_day - 3)
    else:
        price_change = 0
            
    # update price
    headline_move = 0
    if random.random() < 0.02: 
        # Huge Rare event: Tariff (-8%) or AI Hype (+8%)
        headline_move = options_data[0]["x0"] * random.choice([-0.08, 0.08])
    # 0.04/252 = e.g. 4% annual drift converted to new daily price move
    options_data[0]["x0"] += (0.04/252) + price_change + headline_move
            
    # update volatility using percent change
    pct_move = price_change / current_x0
    options_data[0]["vol"] -= (pct_move * sensitivity)
    # small nudge so iv doesn't go to zero or infinity 
    # (drifts back toward starting sigma by 2% each day)
    options_data[0]["vol"] += (iv - options_data[0]["vol"]) * 0.02
            
    # make sure the values are in bounds
    options_data[0]["x0"] = max(0.01, options_data[0]["x0"]) # Price > 0
    options_data[0]["vol"] = max(0.01, options_data[0]["vol"]) # Vol > 0

def inc_currentTime(currentTime, expireTime):
    currentTime = currentTime + 1
    if currentTime == expireTime: 
        currentTime = currentTime - 0.0000000001
    return currentTime

print("\nGraph Data:")
def graph_simulation(colorArray, options_data, expireTime, currentTime):
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
                print("\nLine: " + str(colorArray[i]) + "\nEnd Price: " + str(copy_options_data[0]["x0"]) + "\n" + "End Option Price: " + str(round(option_p,2)))
            
        plt.plot(timeArray, opArray, marker="o", linestyle='-', color=colorArray[i])
        if i == len(colorArray) - 1:
            plt.show()
        else:
            currentTime = int(datetime.datetime.now().strftime("%j"))
            options_data = [
                {"ticker": optionArray[0], 
                "T": (expireTime-currentTime)/365, 
                "K": optionArray[2], 
                "mp": call_price, 
                "vol": iv,
                "x0": tickerInf[1]}
            ]

graph_simulation(colorArray, options_data, expireTime, currentTime)

currentTime = int(datetime.datetime.now().strftime("%j"))
options_data = [
    {"ticker": optionArray[0], 
    "T": (expireTime-currentTime)/365, 
    "K": optionArray[2], 
    "mp": call_price, 
    "vol": iv,
    "x0": tickerInf[1]}
    ]
    
print("\nSimulating 10 to 10,000 different price paths to get an average option price:")
def simulate_option_price(bound, currentTime=currentTime, expireTime=expireTime, options_data=options_data):
    print(f"\n{bound} Price Paths:")
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
            {"ticker": optionArray[0], 
            "T": (expireTime-currentTime)/365, 
            "K": optionArray[2], 
            "mp": call_price, 
            "vol": iv,
            "x0": tickerInf[1]}
        ]    

    averagePrice = round(averagePrice / bound, 2)
    averageOption = round(averageOption / bound, 2)
    print("Results at Expiration:")
    print(f"Average Stock Price: {averagePrice}")
    print(f"Average Call Price: {averageOption}")
    print(f"Number of times reached 0: {times0}")

num_times = 10
while num_times <= 10000:
    simulate_option_price(num_times, currentTime, expireTime, options_data)
    num_times *= 10