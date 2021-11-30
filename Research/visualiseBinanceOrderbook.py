import os
import sqlite3
from sqlite3 import Error
from math import floor
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import cm
import numpy as np
import datetime as datetime
import math

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()
date = "'10-28-2021'"
times = [14, 15, 16, 17]
timesQuery = "(time like '"
for time in times:
    timesQuery += str(time) + "%' or time like '"
timesQuery = timesQuery[:-15]
timesQuery = timesQuery + ")" # or, use this
timesQuery = "time like '2%'"

asks = """Select * from asks where date=""" + date + """ AND """ + timesQuery
cur.execute(asks)
asks = cur.fetchall()
asks = pd.DataFrame(asks, columns=['date', 'time', 'price', 'size'])
print(asks)
bids = """Select * from bids where date=""" + date + """ AND """ + timesQuery
cur.execute(bids)
bids = cur.fetchall()
bids = pd.DataFrame(bids, columns=['date', 'time', 'price', 'size'])
print(bids)

#BBO = pd.DataFrame(columns=['time', 'ask', 'bid'])
askTimes = sorted(set(asks['time']))
bidTimes = sorted(set(bids['time']))
i = 0
oldTime = datetime.datetime.now()

for time in askTimes:
    # price agg: round up to nearest 10 for asks, down for bids. rounding inaccuracy will be <.1% if btc is >10k
    askTimes[i] = pd.DataFrame(asks[asks['time'] == time])
    askTimes[i]['price'] = (askTimes[i]['price'] - askTimes[i]['price'].iloc[0])
    askTimes[i]['price agg'] = [round( (int(x)) /10)*10 for x in askTimes[i]['price']]
    #BBO.loc[i] = [time, asks[asks['time'] == time]['price'][0], 0]
    askTimes[i].drop('price', axis=1, inplace=True)
    askTimes[i] = askTimes[i].groupby('price agg')
    askTimes[i] = askTimes[i].sum()
    askTimes[i].rename(columns={'size': time}, inplace=True)
    i += 1

i = 0
for time in bidTimes:
    bidTimes[i] = pd.DataFrame(bids[bids['time'] == time])
    bidTimes[i]['price'] = (bidTimes[i]['price'] - bidTimes[i]['price'].iloc[0])
    bidTimes[i]['price agg'] = [round( (int(x)) /10)*10 for x in bidTimes[i]['price']]
    bidTimes[i].drop('price', axis=1, inplace=True)
    bidTimes[i] = bidTimes[i].groupby('price agg')
    bidTimes[i] = bidTimes[i].sum()
    bidTimes[i].rename(columns={'size': time}, inplace=True)
    i += 1

asks = pd.concat([x for x in askTimes], axis=1, join='outer')

bids = pd.concat([x for x in bidTimes], axis=1, join='outer')
bids = bids[::-1]
#print(bids)

asks = asks.sub(bids, fill_value=0)
asks = asks[::-1]
#print(asks)
print(datetime.datetime.now() - oldTime)

# may be able to have both on one plot?
#axs = sns.heatmap(pd.concat([asksVisualised, bidsVisualised], axis=0, join='outer'), cmap="Reds", annot=False)
#sns.heatmap(asks, ax=axs[0], cmap="Reds", annot=True, fmt=".0f",
#            annot_kws={'rotation': 45, 'color': 'blue'}, robust=True)

#sns.heatmap(bids, cmap="Blues", mask=bids.isnull(), robust=True)
plt.figure()
sns.heatmap(asks,cmap="coolwarm", center=0, robust=True)
#BBO.plot(x='time', y=['ask'])

#--------

BBO = """Select * from bidDeltas where date=""" + date + """ AND """ + timesQuery
cur.execute(BBO)
BBO = cur.fetchall()
BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bid', 'logBid', 'bidPctChange'])
price = BBO.copy(deep=True)
BBO.set_index('time', inplace=True)
print(BBO)

netTrade = """Select * from tradesFeatures where date=""" + date + """ AND """ + timesQuery
cur.execute(netTrade)
netTrade = cur.fetchall()
netTrade = pd.DataFrame(netTrade, columns=['date', 'time', 'pctBought', 'totalBought', 'totalSold'])
netTrade['netTrade'] = netTrade['totalBought'] - netTrade['totalSold']
netTrade['grossTrade'] = netTrade['totalBought'] + netTrade['totalSold']
netTrade.set_index('time', inplace=True)

minPctIndex = netTrade.nsmallest(10, 'pctBought').index
maxPctIndex = netTrade.nlargest(10, 'pctBought').index
minGrossIndex = netTrade.nsmallest(10, 'grossTrade').index
maxGrossIndex = netTrade.nlargest(10, 'grossTrade').index

VWOrders = """Select * from orderbookFeatures where date=""" + date + """ AND """ + timesQuery
cur.execute(VWOrders)
VWOrders = cur.fetchall()
VWOrders = pd.DataFrame(VWOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])

fig, axs = plt.subplots(2)
#weighted limit orders
axs[0].plot(VWOrders['VWBids'] - price['bid'], label="Bids")
axs[0].plot(VWOrders['VWAsks'] - price['bid'], label="Asks")
axs[0].legend(loc="upper left")
axs[0].xaxis.set_visible(False)

axs[1].plot(BBO['bid'])
axs[1].tick_params(axis='x', rotation=90)

plt.show()