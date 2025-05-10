import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

BBO = """Select * from bidDeltas"""
cur.execute(BBO)
BBO = cur.fetchall()
BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bid', 'logBid', 'bidPctChange'])

VWOrderbook = """Select * from orderbookFeatures order by date"""
cur.execute(VWOrderbook)
VWOrderbook = cur.fetchall()
VWOrders = pd.DataFrame(VWOrderbook, columns=['date', 'time', 'VWBids', 'VWAsks'])
BBO['VWBids'] = VWOrders['VWBids']
BBO['VWAsks'] = VWOrders['VWAsks']
print(BBO)

asks = BBO[ (BBO['bid'] > BBO['VWAsks'].shift(1)) ]
bids = BBO[ (BBO['bid'] < BBO['VWBids'].shift(1))  ]

print(bids)
print(asks)

fig, axs = plt.subplots(2)
axs[0].plot(BBO['bid'])
axs[1].plot(VWOrders['VWBids'] - BBO['bid'])
axs[1].plot(VWOrders['VWAsks'] - BBO['bid'])
axs[1].axhline(y=0, color='g', linestyle='--')


FMA = 144
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=FMA)
BBO['FMA'] = BBO['bidPctChange'].rolling(window=indexer).std()

plt.figure()
plt.scatter(VWOrders['VWBids'] - BBO['bid'], BBO['FMA'])
plt.scatter(VWOrders['VWAsks'] - BBO['bid'], BBO['FMA'])

plt.show()
