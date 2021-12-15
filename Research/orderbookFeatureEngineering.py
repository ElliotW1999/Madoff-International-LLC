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
#dates = ["'08-20-2021'", "'08-21-2021'", "'08-22-2021'", "'08-23-2021'", "'08-24-2021'", "'08-25-2021'", "'08-26-2021'",
#         "'08-27-2021'", "'08-28-2021'", "'08-29-2021'", "'08-30-2021'", "'08-31-2021'",
#         "'09-01-2021'", "'09-02-2021'", "'09-03-2021'", "'09-04-2021'", "'09-05-2021'", "'09-06-2021'", "'09-07-2021'",
#         "'09-08-2021'", "'09-09-2021'", "'09-10-2021'", "'09-11-2021'", "'09-12-2021'", "'09-13-2021'", "'09-14-2021'",
#         "'09-15-2021'", "'09-16-2021'", "'09-17-2021'", "'09-18-2021'", ]
#            "'09-20-2021'" #, "'09-21-2021'",
#         "'09-22-2021'", "'09-23-2021'", "'09-24-2021'", "'09-25-2021'", "'09-26-2021'", "'09-27-2021'", "'09-28-2021'",
#         "'09-29-2021'", "'09-30-2021'",
#         "'10-01-2021'", "'10-02-2021'", "'10-03-2021'", "'10-04-2021'", "'10-05-2021'", "'10-06-2021'", "'10-07-2021'",
#         "'10-08-2021'", "'10-09-2021'", "'10-10-2021'", "'10-11-2021'", "'10-12-2021'", "'10-13-2021'", "'10-14-2021'",
#         "'10-15-2021'", "'10-16-2021'", "'10-17-2021'", "'10-18-2021'", "'10-19-2021'", "'10-20-2021'", "'10-21-2021'",
#         "'10-22-2021'", "'10-23-2021'", "'10-24-2021'", "'10-25-2021'", "'10-26-2021'", "'10-27-2021'", "'10-28-2021'",
#         "'10-29-2021'",
#         "'10-30-2021'", "'10-31-2021'", "'11-01-2021'", "'11-02-2021'", "'11-03-2021'", "'11-04-2021'", "'11-05-2021'",
#         "'11-06-2021'",
#         "'11-07-2021'", "'11-08-2021'", "'11-09-2021'", "'11-10-2021'", "'11-11-2021'", "'11-12-2021'","'11-13-2021'",
#dates =["'11-14-2021'", "'11-15-2021'", "'11-16-2021'", "'11-17-2021'", "'11-18-2021'", "'11-19-2021'", "'11-20-2021'"]
#dates = ["'11-21-2021'", "'11-22-2021'", "'11-23-2021'", "'11-24-2021'", "'11-25-2021'", "'11-26-2021'", "'11-27-2021'", "'11-28-2021'"]
#dates = ["'11-29-2021'", "'11-30-2021'", "'12-01-2021'", "'12-02-2021'", "'12-03-2021'", "'12-04-2021'"]
dates = ["'12-05-2021'", "'12-06-2021'", "'12-07-2021'", "'12-08-2021'", "'12-09-2021'", "'12-10-2021'",  "'12-11-2021'"]

### ------
### Trades
for date in dates:
    trades = """Select * from trades where date=""" + date
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
    asks = """Select * from asks where date=""" + date + """ and rowid%5000== 1 """
    cur.execute(asks)
    asks = cur.fetchall()
    asks = pd.DataFrame(asks, columns=['date', 'time', 'asks', 'size'])
    asks.drop(['date', 'time', 'size'], axis=1, inplace=True)

    bids = """Select * from bids where date=""" + date + """ and rowid%5000== 1 """
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
    bids = """Select * from bids where date=""" + date
    cur.execute(bids)
    bids = cur.fetchall()
    bids = pd.DataFrame(bids, columns=['date', 'time', 'price', 'size'])
    times = sorted(set(bids['time']))

    asks = """Select * from asks where date=""" + date
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