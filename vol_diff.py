# Graph comparing the yfinance IV with the getcloseIV (historical IV) 
#  I calculate by taking the last year of prices of the stock (referencing code from compute_vols.py) 
# and make an analysis on each affects the calculated black-scholes price and the market price.




# results = []
# for option in options_data:
#     tickerName = option["ticker"]
#     T = float(option["T"])
#     K = float(option["K"])
#     mp = float(option["mp"])

#     x0 = float(option["x0"])
#     sigma = float(option["vol"])

#     option_price = calc_op(x0, K, 0.04, sigma, T)
#     diff = option_price - mp

#     results.append({
#         "ticker": tickerName,
#         "T_years": round(T, 4),
#         "K": round(K, 2),
#         "x0": round(x0, 2),
#         "sigma": round(sigma, 3),
#         "market_price": round(mp, 4),
#         "calc_option_price": round(option_price, 4),
#         "model_minus_market": round(diff, 4),
#     })

# df_res = pd.DataFrame(results)
# print("\nFull Black–Scholes results for options:\n")
# print(df_res[["ticker", "T_years", "K", "x0", "sigma",
#               "market_price", "calc_option_price", "model_minus_market"]].to_string(index=False))
