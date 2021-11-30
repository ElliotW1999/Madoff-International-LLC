import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import datetime as datetime

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

price = """Select * from bidDeltas where date='09-07-2021' and time like '1%' """
cur.execute(price)
price = cur.fetchall()
price = pd.DataFrame(price, columns=['date', 'time', 'bid', 'logBid', 'bidPctChange'])
price.drop(['logBid', 'bidPctChange'], axis=1, inplace=True)

weightedOrders = """Select * from orderbookFeatures where date='09-07-2021' and time like '1%' order by date"""
cur.execute(weightedOrders)
weightedOrders = cur.fetchall()
weightedOrders = pd.DataFrame(weightedOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])
weightedOrders['VWBids'] = weightedOrders['VWBids'] - price['bid']
weightedOrders['VWAsks'] = weightedOrders['VWAsks'] - price['bid']

fig, ax = plt.subplots(2)

ax[0].plot(price['bid'])
ax[1].plot(weightedOrders['VWBids'])
ax[1].plot(weightedOrders['VWAsks'])
ax[0].legend(['price'])
ax[1].legend(['weighted bids', 'weighted asks'])
plt.show()


