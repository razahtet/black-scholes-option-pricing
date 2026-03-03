# Black-Scholes Option Pricing Simulation
Using the black-scholes formula, the price of a European Buy Call is calculated to simulate random price paths of the option where traders can look at and analyze to see if it could possibly be profitable.

## Overview
* Users would be interested in seeing how the future of the option price plays out with the Monte Carlo simulation to see how profitable the buy call could be.
* Analyzing why implied volatility is important in buying the option vs using historical volatility.

## Directory Structure
```
├── price_buy_call.py
├── compute_vols.py 
├── price_call_debit_spread.py       
└── vol_diff.py       
```

## Calculations
<ul>
    <li><strong>Using the Black-Scholes formula, the price of a European Buy Call is calculated.</strong>
        <ul>
            <li><strong>It is calculated using:</strong>
                <ul>
                    <li>Implied Volatility (IV) from the <em>yfinance</em> API (σ)</li>
                    <li>Last Closing Price of the stock when extracting the data (x₀)</li>
                    <li>The current # of days until expiration (DTE) divided by 365 (T)</li>
                    <li>The strike price of the option (K)</li>
                    <li>The risk-free interest rate, where I used 4% (a)</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

<hr>

<h3 id="fixes">Some Minor Problems and Their Fixes</h3>
<ul>
    <li><strong><em>yfinance</em> IV Issues:</strong> When the market is closed, the <em>yfinance</em> IV often becomes less than 0.00001, and bid/ask prices frequently drop to 0.</li>
    <li><strong>The Fix (Backwards IV):</strong> To calculate an accurate option price, the IV is calculated "backwards" using the <strong>Bisection Method</strong>. The algorithm starts searching within a range (e.g., up to 500%) and iteratively inputs values into the formula until it finds an IV where the <strong>calculated option price</strong> equals the <strong>last option price</strong> fetched from <em>yfinance</em>.</li>
</ul>

<hr>

<h3 id="formula">Option Pricing Formula</h3>

<p align="center">
  $$c = x_0 \phi(\sigma\sqrt{T} + b) - Ke^{-aT}\phi(b)$$
</p>

<p><strong>Where:</strong></p>

<p align="center">
  $$b = \frac{\ln(x_0/K) + (a - \sigma^2/2)T}{\sigma\sqrt{T}}$$
</p>

<p><strong>In this formula:</strong></p>
<ul>
    <li>φ denotes the standard normal cumulative distribution function.</li>
    <li>σ is the volatility of the stock.</li>
    <li>K is the strike price.</li>
    <li>a is the interest rate.</li>
    <li>T is the time to expiration in years.</li>
</ul>

## Simulations
* The simulation for the random price movement for the day:
   * A random number generator from 1-6 describing the day:
        * 0: no change
        * 1: up a little bit
        * 2: up a good amount
        * 3: up a lot higher than usual (e.g. earnings beat)
        * 4: down a little bit
        * 5: down a good amount
        * 6: down a lot lower than usual (e.g. earnings miss)
    * The price change is then calculated by 0.5 * the IV * that random number (4-6 makes the 0.5 negative).
    * Sensitivity is also included to update the stock's volatility every day:
        * When the stock is up or down a lot, sensitivity will be higher especially if there are major news.
        * Sensitivity will be a lot less if there are no news on a certain day.
    * There is also a 2% chance of a major headline event on a random day, making the stock go down or up drastically combined with the movement from the random number generator.
    * IV is also nudged a bit everyday so it doesn't reach zero or infinity during simulations.

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
   * price_buy_call.py is the main file to see the simulations and the random price paths of the calculated option in play.
      * python price_buy_call.py
   * compute_vols.py is the file for calculating the historical volatility of a stock for a time period, with 1 year as the default.
      * python compute_vols.py

## Features
- price_buy_call.py: Graph of Monte Carlo Simulations for the stock and its specific buy call and In-Depth Analysis of the # of times the option reached 0 at expiration, its average option price, and the average stock price over 10 to 10K iterations.
- compute_vols.py: List of calculated historical volatilities and their last closing prices for stocks.

## In-progress
- Currently working on analyzing the effects of Implied Volatility (IV) and Historical Volatility on option and market prices and calculating the option price for a call debit spread and simulating it.
- Replace the random number generator for the random price movement on a simulated day with brownian motion.
