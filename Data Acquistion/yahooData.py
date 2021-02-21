from yahoofinancials import YahooFinancials  # use for fundamental data
import yfinance as yf                        # use for price data
import os
import requests
import sqlite3
from sqlite3 import Error

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

# TODO: find volatility/ volume for past 6(/5?) days at minute frequency,
#  and today's openPricesing + T-15m price and T-15m volume
#  We use historical minute freq as it costs 50 credits/ day, whereas EOD is 10 credits/ day (more data)
#response = requests.get("https://cloud.iexapis.com/stable/stock/twtr/chart/1m?token=pk_9b06c71058734e26b123ee57be97768a")
response = requests.get("https://sandbox.iexapis.com/stable/stock/pltr/chart/5dm?token=Tsk_f886b230904e46b3ae90e31c6bf195ef")
#response = requests.get("https://cloud.iexapis.com/stable/stock/pltr/chart/5dm?token=pk_9b06c71058734e26b123ee57be97768a")
# don't use my goddamn API key

date = []
openPrices = []
highPrices = []
lowPrices = []
closePrices = []
volume = []
for line in response.json():
    date.append(line['date'])
    openPrices.append(line['open'])
    highPrices.append(line['high'])
    lowPrices.append(line['low'])
    closePrices.append(line['close'])
    volume.append(line['volume'])
print(type(closePrices[0]))

db_file = os.path.dirname(os.path.dirname( __file__ ))+"/Data/tickers.db"

print(db_file)
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

print(date[0])
for i in range(0,len(volume)):
    sqlite_insert_with_param = """INSERT INTO price (date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?);"""
    data_tuple = ("2021-02-12", openPrices[i], highPrices[i], lowPrices[i], closePrices[i], volume[i])
    cur.execute(sqlite_insert_with_param, data_tuple)
#conn.commit()
