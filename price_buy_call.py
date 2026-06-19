import math
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
import matplotlib.pyplot as plt
from compute_vols import get_vol_close
from formulas import get_IV_mp, graph_simulation, simulate_option_price


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

# Example:
# PLTR 145C Expiring July 17, 2026
currentTime = int(datetime.datetime.now().strftime("%j"))
dateA = optionArray[1].split("-")
expireTime = int(datetime.datetime(int(dateA[0]), int(dateA[1]), int(dateA[2])).strftime("%j"))
# for t in tickers:
tickerInf = get_vol_close(optionArray[0])
target_date = optionArray[1]

iv_mp = get_IV_mp(optionArray[0], target_date, optionArray[2], 0.04, (expireTime-currentTime)/365, tickerInf[1])
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

print("\nGraph Data:")

graph_simulation(colorArray, options_data, expireTime, currentTime, iv)

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

num_times = 10
while num_times <= 10000:
    simulate_option_price(num_times, currentTime, expireTime, options_data, iv)
    num_times *= 10