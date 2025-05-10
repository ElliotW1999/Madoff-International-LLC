import os
import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()
# currently missing 09-19-2021
#dates = ["'2022-01-16'", "'2022-01-17'", "'2022-01-18'"]
dates = ["'2023-07-23'"]

### ------
### Trades
for date in dates:
    trades = """Select * from trades2023 where date=""" + date
    cur.execute(trades)
    trades = cur.fetchall()
    trades = pd.DataFrame(trades, columns=['date', 'time', 'isBuyerMaker', 'price', 'size'])
    date = trades['date'][0]
    trades.drop(['date', 'price'], axis=1, inplace=True)
    print(trades)
    times = sorted(set(trades['time']))

    # features inc. % bought, total bought, total sold
    for time in times:
       marketBuys = trades.query('isBuyerMaker==1 and time=='+"'"+ time +"'")
       totalBought = marketBuys['size'].sum()
       pctBought = len(marketBuys.index)
       marketSells = trades.query('isBuyerMaker==0 and time=='+"'"+ time +"'")
       totalSold = marketSells['size'].sum()
       sqlite_insert_with_param = """INSERT INTO tradesFeatures (date, time, pctBought, totalBought, totalSold) VALUES (?, ?, ?, ?, ?);"""
       data_tuple = (date, time, pctBought, totalBought, totalSold)
       cur.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

### ---
### BBO
for date in dates:
    asks = """Select * from asks2023 where date=""" + date + """ and rowid%5000== 1 """
    cur.execute(asks)
    asks = cur.fetchall()
    asks = pd.DataFrame(asks, columns=['date', 'time', 'asks', 'size'])
    asks.drop(['date', 'time', 'size'], axis=1, inplace=True)

    bids = """Select * from bids2023 where date=""" + date + """ and rowid%5000== 1 """
    cur.execute(bids)
    bids = cur.fetchall()
    bids = pd.DataFrame(bids, columns=['date', 'time', 'bids', 'size'])
    date = bids['date'][0]
    bids.drop(['size'], axis=1, inplace=True)

    BBO = pd.concat([bids, asks], axis=1)
    print(date)
    for index, row in BBO.iterrows():
        print(row['time'])
        sqlite_insert_with_param = """INSERT INTO BBO (date, time, bestBid, bestAsk) VALUES (?, ?, ?, ?)"""
        data_tuple = (date, row['time'], row['bids'], row['asks'])
        cur.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()


### ---------
### bidDeltas
for date in dates:
    BBO = """Select * from BBO where date=""" + date
    cur.execute(BBO)
    BBO = cur.fetchall()
    BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bids', 'asks'])

    lastDelta = """Select * from bidDeltas ORDER BY rowid DESC LIMIT 1"""  # use this to extend existing biddeltas
    cur.execute(lastDelta)
    lastDelta = cur.fetchone()
    lastDelta = pd.Series(lastDelta)
    lastDelta = pd.DataFrame(lastDelta.values.reshape(1, 5), columns=['date', 'time', 'bids', 'logBid', 'bidPctChange'])
    lastDelta.drop(['logBid', 'bidPctChange'], axis=1, inplace=True)

    BBO = pd.concat([lastDelta, BBO])
    BBO.drop('asks', axis=1, inplace=True)
    BBO['logBid'] = np.log(BBO['bids'].astype('float')) - np.log(BBO['bids'].shift(1).astype('float'))
    BBO['bidPctChange'] = BBO['bids'].pct_change()
    BBO.dropna(axis=0, inplace=True)
    print(BBO)

    date = BBO['date'][0]
    for index, row in BBO.iterrows():
        sqlite_insert_with_param = """INSERT INTO bidDeltas (date, time, bid, logBid, bidPctChange) VALUES (?, ?, ?, ?, ?)"""
        data_tuple = (date, row['time'], row['bids'], row['logBid'], row['bidPctChange'])
        cur.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()


### -----------------
### OrderbookFeatures
for date in dates:
    bids = """Select * from bids2023 where date=""" + date
    cur.execute(bids)
    bids = cur.fetchall()
    bids = pd.DataFrame(bids, columns=['date', 'time', 'price', 'size'])
    times = sorted(set(bids['time']))

    asks = """Select * from asks2023 where date=""" + date
    cur.execute(asks)
    asks = cur.fetchall()
    asks = pd.DataFrame(asks, columns=['date', 'time', 'price', 'size'])
    date = bids['date'][0]

    bids['weightedPriceBids'] = (bids['price'].multiply(bids['size']))
    bids = bids.groupby(by=['time']).sum()
    bids['weightedPriceBids'] = bids['weightedPriceBids'].divide(bids['size'])
    bids.drop(['price', 'size'], axis=1, inplace=True)

    asks['weightedPriceAsks'] = (asks['price'].multiply(asks['size']))
    asks = asks.groupby(by=['time']).sum()
    asks['weightedPriceAsks'] = asks['weightedPriceAsks'].divide(asks['size'])
    asks.drop(['price', 'size'], axis=1, inplace=True)

    bids = pd.concat([bids, asks], axis=1)
    print(bids)
    print(date)

    for time in times:
        df = pd.DataFrame(bids[bids.index == time])
        #print(df)
        sqlite_insert_with_param = """INSERT INTO orderbookFeatures (date, time, VWBids, VWAsks) VALUES (?, ?, ?, ?);"""
        data_tuple = (date, time, df['weightedPriceBids'][0], df['weightedPriceAsks'][0])
        cur.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()