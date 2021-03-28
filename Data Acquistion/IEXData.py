import os
import requests
import sqlite3
from sqlite3 import Error

# TODO: find volatility/ volume for past 6(/5?) days at minute frequency,
#  and today's openPricesing + T-15m price and T-15m volume
#  We use historical minute freq as it costs 50 credits/ day, whereas EOD is 10 credits/ day (more data)
symbol_id = "pltr"
#response = requests.get("https://cloud.iexapis.com/stable/stock/twtr/chart/1m?token=pk_9b06c71058734e26b123ee57be97768a")
response = requests.get("https://sandbox.iexapis.com/stable/stock/" + symbol_id + "/chart/5dm?token=Tsk_f886b230904e46b3ae90e31c6bf195ef")
#response = requests.get("https://cloud.iexapis.com/stable/stock/pltr/chart/5dm?token=pk_9b06c71058734e26b123ee57be97768a")
# don't use my goddamn API key

priceDate = []
openPrices = []
highPrices = []
lowPrices = []
closePrices = []
volume = []
for line in response.json():
    priceDate.append(line['date'])
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

for i in range(0,len(volume)):
    sqlite_insert_with_param = """INSERT INTO dailyPriceData (symbol_id, price_date, open, high, low, close, volume) 
    VALUES (?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (symbol_id, priceDate[i], openPrices[i], highPrices[i], lowPrices[i], closePrices[i], volume[i])
    cur.execute(sqlite_insert_with_param, data_tuple)
#conn.commit()
# TODO: unhighlight this line above to add data to db^