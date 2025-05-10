# Buy on VWOrders[(VWOrders['VWBids'] - BBO['bid']) < -1800] or netTrade[netTrade['netTrade'] > 55
# Sell on netTrade[netTrade['netTrade'] < -55 or netTrade[netTrade['pctBought'] < 100

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
from pathlib import Path

p = Path(__file__).parents[2]
print(p)
db_file = str(p) + "/Data/binanceData.db"
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
BBO['12HrChange'] = (BBO['bid'].shift(-48) - BBO['bid']) / BBO['bid'] * 100
FMA = 144
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=FMA)
BBO['avgChange_'+str(FMA)] = BBO['logBid'].rolling(window=indexer).sum()
print(BBO.head())

netTrade = """Select * from tradesFeatures"""
cur.execute(netTrade)
netTrade = cur.fetchall()
netTrade = pd.DataFrame(netTrade, columns=['date', 'time', 'pctBought', 'totalBought', 'totalSold'])
netTrade['netTrade'] = netTrade['totalBought'] - netTrade['totalSold']
netTrade['grossTrade'] = netTrade['totalBought'] + netTrade['totalSold']

VWOrders = """Select * from orderbookFeatures order by date"""
cur.execute(VWOrders)
VWOrders = cur.fetchall()
VWOrders = pd.DataFrame(VWOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])
priceAdjustedOrders = pd.DataFrame(VWOrders['VWBids'] - BBO['bid'], columns=['bids'])
priceAdjustedOrders['asks'] = VWOrders['VWAsks'] - BBO['bid']

window = 144
priceAdjustedAsks_mean = priceAdjustedOrders['asks'].rolling(window=window).mean()
priceAdjustedAsks_std = priceAdjustedOrders['asks'].rolling(window=window).std()
priceAdjustedOrders['asks_zscore'] = (priceAdjustedOrders['asks'] - priceAdjustedAsks_mean)/priceAdjustedAsks_std
priceAdjustedOrders['asks_zscore'].fillna(0, inplace=True)

priceAdjustedBids_mean = priceAdjustedOrders['bids'].rolling(window=window).mean()
priceAdjustedBids_std = priceAdjustedOrders['bids'].rolling(window=window).std()
priceAdjustedOrders['bids_zscore'] = (priceAdjustedOrders['bids'] - priceAdjustedBids_mean)/priceAdjustedBids_std
priceAdjustedOrders['bids_zscore'].fillna(0, inplace=True)

myTrades = BBO.copy(deep=False)
myTrades.drop(['bid', 'logBid', 'bidPctChange', '12HrChange'], axis=1, inplace=True)
myTrades.loc[:, 'position'] = 0

test = pd.Series(VWOrders[priceAdjustedOrders['asks'] > 1500].index + 144)
test = test[test < len(BBO['bid'])]

myTrades.loc[:, 'position'] = 1 # buy
myTrades.loc[test, 'position'] = 2 # sell
print(myTrades)

print(myTrades)
print(sum(myTrades['position']))

f, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1]})
axs[0].scatter(netTrade[netTrade['netTrade'] < -55].index,
               BBO.loc[netTrade[netTrade['netTrade'] < -55].index]['bid'], c='red', marker='x')
axs[0].scatter(netTrade[netTrade['pctBought'] < 200].index,
               BBO.loc[netTrade[netTrade['pctBought'] < 200].index]['bid'], c='blue', marker='x')
axs[0].scatter(VWOrders[priceAdjustedOrders['asks'] > 1500].index,
               BBO.loc[VWOrders[priceAdjustedOrders['asks'] > 1500].index]['bid'], c='black', marker='x')

#axs[0].scatter(VWOrders[VWOrders['VWBids'] - BBO['bid'] > -300].index,
#               BBO.loc[VWOrders[VWOrders['VWBids'] - BBO['bid'] > -300].index]['bid'], c='violet', marker='x')

#plt.scatter(netTrade[netTrade['netTrade'] > 65].index,
#            BBO.loc[netTrade[netTrade['netTrade'] > 65].index]['bid'], c='blue', marker='x')
axs[0].plot(BBO['bid'], 'g', linestyle='--', linewidth=.2)
axs[0].plot(VWOrders['VWBids'] , 'r', linestyle='--', linewidth=.2)
axs[0].plot(VWOrders['VWAsks'] , 'b', linestyle='--', linewidth=.2)

axs[1].plot( (VWOrders.mask(priceAdjustedOrders['bids'] > -800, BBO['bid'], axis=0)['VWBids'] - BBO['bid']) )
axs[1].plot( (VWOrders.mask(priceAdjustedOrders['asks'] < 1500, BBO['bid'], axis=0)['VWAsks'] - BBO['bid']), label="Asks")

plt.figure()
print(VWOrders[priceAdjustedOrders['bids'] < -1500])
sns.distplot(BBO.loc[VWOrders[priceAdjustedOrders['asks'] > 1500].index]['12HrChange'],
                                            bins=500, hist=False, label='buy signal')
print(len(BBO.loc[netTrade[netTrade['pctBought'] < 200].index & netTrade[netTrade['netTrade'] < -50].index]))
sns.distplot(BBO.loc[netTrade[netTrade['pctBought'] < 200].index & netTrade[netTrade['netTrade'] < -50].index]['12HrChange'],
                                            bins=500, hist=False, label='sell signal')
sns.distplot(BBO['12HrChange'],
                                            bins=500, hist=False, label='buy and hold')
plt.legend(loc='upper right')
f, axs2 = plt.subplots(3)
axs2[0].plot(BBO['bid'])
axs2[1].plot(priceAdjustedOrders.mask(priceAdjustedOrders['asks_zscore'] < 2.5, 0)['asks_zscore'])
axs2[2].plot(priceAdjustedOrders.mask(priceAdjustedOrders['bids_zscore'] > -3, 0)['bids_zscore'])

plt.figure()
sns.distplot(BBO[netTrade['netTrade'] > -50]['avgChange_'+str(FMA)], bins=500, hist=False)
sns.distplot(BBO[netTrade['netTrade'] < -50]['avgChange_'+str(FMA)], bins=500, hist=False)
plt.figure()
plt.scatter(BBO['avgChange_'+str(FMA)], netTrade['netTrade'] < -50)
plt.show()
