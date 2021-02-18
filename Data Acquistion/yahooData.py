import datetime
from yahoofinancials import YahooFinancials  # use for fundamental data
import yfinance as yf                        # use for price data
import pandas as pd
import numpy as np
import requests
#import pyqtgraph #switch to pyqtgraph eventually...
import matplotlib.pyplot as plt

ticker = "SPY AAPL MSFT"
data = yf.download(  # or pdr.get_data_yahoo(...
    # tickers list or string as well
    tickers = 'TSLA',

    # use "period" instead of start/end
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # (optional, default is '1mo')
    period = "5d",

    # fetch data by interval (including intraday if period < 60 days)
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # (optional, default is '1d')
    interval = "90m",

    # group by ticker (to access via data['SPY'])
    # (optional, default is 'column')
    group_by = 'ticker',

    # adjust all OHLC automatically
    # (optional, default is False)
    auto_adjust = True,

    # download pre/post regular market hours data
    # (optional, default is False)
    prepost = True,

)
print(len(data))
#print(data)

# TODO: find volatility/ volume for past 6(/5?) days at minute frequency,
#  and today's opening + T-15m price and T-15m volume
#  We use historical minute freq as it costs 50 credits/ day, whereas EOD is 10 credits/ day (more data)
#response = requests.get("https://cloud.iexapis.com/stable/stock/twtr/chart/1m?token=pk_9b06c71058734e26b123ee57be97768a")
response = requests.get("https://sandbox.iexapis.com/stable/stock/gme/chart/5dm?token=Tsk_f886b230904e46b3ae90e31c6bf195ef")
closePrices = []
volume = []
for line in response.json():
    closePrices.append(line['close'])
    volume.append(line['volume'])
    print(line['volume'])
print(len(response.json()))

# Have to investigate using ATR vs historical volatility, using the latter for now
print(closePrices)
logReturns = np.array([round(np.log(j/i), 3) for i, j in zip(closePrices[:-1], closePrices[1:])]) # np.log(j/i) - 1 ?


periodsRoot = 14 # 14^2 = 196 which ~= 195. This makes computation faster
volumeAvg = np.median(volume)                                 # we use the median because the data is strongly skewed
volumeDeviation = np.mean(np.absolute(volume - volumeAvg))    # std dev is not used as the data is skewed
print(volumeDeviation)
test = [volume.index(i) for i in volume if i > volumeAvg + (5*volumeDeviation)]
print(test)

fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(volume)
axs[1, 0].plot(closePrices)
axs[0, 1].hist(volume, 25)
axs[1, 1].hist(closePrices, 25)
axs[0, 0].set_title("Time-series")
axs[0, 0].set(ylabel="Volume")
axs[0, 1].set_title("Histogram")
axs[1, 0].set(ylabel="Price")
plt.show()
