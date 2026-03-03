# Black-Scholes Option Pricing Simulation
Using the black-scholes formula, the price of a European Buy Call is calculated to simulate random price paths of the option where traders can look at and analyze to see if it could possibly be profitable.

## Table of Contents
- [About](#about)
- [Calculations](#calculations)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [In-Progress](#In-progress)

## About
- Users would be interested in seeing how the future of the option price plays out with the Monte Carlo simulation
- Analyzing why implied volatility is important in buying the option vs using historical volatility.

## Calculations
* Using the black-scholes formula, the price of a European Buy Call is calculated.
    * It is calculated using:
        * Implied Volatility (IV) from the *yfinance* API. (*sigma*)
        * Last Closing Price of the Stock when extracting the data. (*x0*)
        * The current # of days until expiration (DTE). (*T*)
        * The strike price of the option. (*K*)
        * The risk-free rate, where I used 4%. (*a*)
    * Some Minor Problems and Their Fixes
        * *yfinance* IV becomes less than 0.00001 and bid and ask prices all become 0 when the market is closed.
        * To calculate the option price using the black-scholes formula, IV is calculated "backwards" using the bisection method, where we calculate the IV starting from the mid-range of 500% and input it in the formula multiple times until we get an IV where the calculated option price is equal to the last option price fetched from *yfinance*.

## Installation
Step-by-step instructions to set up the project:
1. Clone the repository:
```bash
git clone https://github.com/razahtet/black-scholes-option-pricing.git
```

2. Navigate to the project directory:
```bash
cd black-scholes-option-pricing
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
- For now:
    * price_buy_call.py is the main file to see the simulations and the random price paths of the calculated option in play.
        * python price_buy_call.py
    * compute_vols.py is the file for calculating the historical volatility of a stock for a time period, with 1 year as the default
        * python compute_vols.py

## Features
- price_buy_call.py: Graph of Monte Carlo Simulations for the stock and its specific buy call and In-Depth Analysis of the # of times the option reached 0 at expiration, its average option price, and the average stock price over a # of iterations ranging from 10 to 10K.
- compute_vols.py: List of calculated historical volatilities and their last closing prices for stocks.

## In-progress
- Currently working on analyzing the effects of Implied Volatility (IV) and Historical Volatility on option and market prices and calculating the option price for a call debit spread and simulating it.
