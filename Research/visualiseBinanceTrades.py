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

date = "'11-26-2021'" # or 0 for all times
#date = 0
if date != 0:
    BBO = """Select * from bidDeltas where date = """ + date
else:
    BBO = """Select * from bidDeltas"""

cur.execute(BBO)
BBO = cur.fetchall()
BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bid', 'logBid', 'bidPctChange'])
FMA = 48
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=FMA)
BBO['drawdown'+str(FMA)] = BBO['bid'] - BBO['bid'].rolling(window=indexer).min()
BBO['drawdown'+str(FMA)].fillna(0, inplace=True)
pctChangeFMAScaled = (BBO['drawdown'+str(FMA)] - BBO['drawdown'+str(FMA)].min() )/\
                     (BBO['drawdown'+str(FMA)].max() - BBO['drawdown'+str(FMA)].min() ) # range 0-1
print(BBO)

if date != 0:
    netTrade = """Select * from tradesFeatures where date = """ + date
else:
    netTrade = """Select * from tradesFeatures """

cur.execute(netTrade)
netTrade = cur.fetchall()
netTrade = pd.DataFrame(netTrade, columns=['date', 'time', 'pctBought', 'totalBought', 'totalSold'])
print(netTrade)
netTrade['netTrade'] = netTrade['totalBought'] - netTrade['totalSold']
netTrade['grossTrade'] = netTrade['totalBought'] + netTrade['totalSold']
#netTrade['datetime'] = str(netTrade['date']) + ' ' + str(netTrade['time'])
#netTrade.set_index('datetime', drop=True, inplace=True)

minPctIndex = netTrade.nsmallest(10, 'pctBought').index
maxPctIndex = netTrade.nlargest(10, 'pctBought').index
minGrossIndex = netTrade.nsmallest(10, 'grossTrade').index
maxGrossIndex = netTrade.nlargest(10, 'grossTrade').index
print(len(BBO)*.003 )
maxNegChange = BBO.nlargest(len(BBO), 'drawdown'+str(FMA)).index # change these to a threshold?
maxNegChange = BBO[BBO['drawdown'+str(FMA)] > 2500].index
print(BBO.loc[maxNegChange])
print(set(BBO.loc[maxNegChange]['date']))

if date != 0:
    VWOrders = """Select * from orderbookFeatures where date = """ + date #+ """ order by date"""
else:
    VWOrders = """Select * from orderbookFeatures order by date"""

cur.execute(VWOrders)
VWOrders = cur.fetchall()
VWOrders = pd.DataFrame(VWOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])

# if overnight
#VWOrders = VWOrders[int(len(VWOrders)/4): -int(len(VWOrders)/4)]
#BBO = BBO[int(len(BBO)/4): -int(len(BBO)/4)]
#netTrade = netTrade[int(len(netTrade)/4): -int(len(netTrade)/4)]

fig, axs = plt.subplots(4)
#f, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})

#weighted limit orders
axs[0].plot(VWOrders['VWBids'] - BBO['bid'], label="Bids") # Unfiltered
axs[0].plot(VWOrders['VWAsks'] - BBO['bid'], label="Asks")
#axs[0].plot( (VWOrders.mask(VWOrders['VWBids'] - BBO['bid'] > -800, BBO['bid'], axis=0)['VWBids'] - BBO['bid']), label="Bids") # Filtered
#axs[0].plot( (VWOrders.mask(VWOrders['VWAsks'] - BBO['bid'] < 800, BBO['bid'], axis=0)['VWAsks'] - BBO['bid']), label="Asks")
axs[0].legend(loc="upper left")
axs[0].xaxis.set_visible(False)

#pctBought
axs[1].plot(netTrade['pctBought'])
axs[1].plot([netTrade.index[0], netTrade.index[-1]], [500, 500], 'r--')
#axs[1].plot([0, len(BBO['bid'])], [700, 700], 'r--')
#axs[1].plot([0, len(BBO['bid'])], [300, 300], 'r--')
#axs[1].plot( (netTrade.mask(np.logical_and(netTrade['pctBought'] > 350, netTrade['pctBought'] < 650), 500)['pctBought'])) # Filtered
axs[1].xaxis.set_visible(False)

#netTrade
axs[2].plot(netTrade['netTrade'])
axs[2].plot([netTrade.index[0], netTrade.index[-1]], [0, 0], 'r--')
#axs[2].plot(BBO['drawdown'+str(FMA)])
#axs[2].plot([0, len(BBO['bid'])], [15, 15], 'r--')
#axs[2].plot([0, len(BBO['bid'])], [-15, -15], 'r--')
#axs[2].plot( (netTrade.mask(np.logical_and(netTrade['netTrade'] > -15, netTrade['netTrade'] < 15) , 0)['netTrade'])) # Filtered
axs[2].xaxis.set_visible(False)

# Price
axs[3].plot(BBO['bid'])
axs[3].tick_params(axis='x', rotation=90)


plt.figure()
plt.hist(pctChangeFMAScaled, bins=1000)
plt.figure()
plt.hist(netTrade['pctBought'], bins=300)
plt.figure()
plt.hist(netTrade['netTrade'], bins=1000)
plt.figure()
plt.hist(VWOrders['VWBids'] - BBO['bid'], bins=1000)
plt.figure()
plt.hist(VWOrders['VWAsks'] - BBO['bid'], bins=1000)
plt.show()

# Test code:
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
#plt.gcf().autofmt_xdate()
#axs[1].scatter(BBO.index, pctChangeFMAScaled,
#               c=cm.Reds( pctChangeFMAScaled), edgecolor='none') #'r--'
#plt.xticks(rotation=60)
#axs.xaxis.set_major_locator(plt.MaxNLocator(9994))

#axs[0].plot(VWOrders[(VWOrders['VWBids'] - BBO['bid'] < -900)]['VWBids'] - BBO['bid'], label="Bids")
#axs[0].plot(VWOrders[(VWOrders['VWAsks'] - BBO['bid'] > 900)]['VWAsks'] - BBO['bid'], label="Asks")
#axs[1].plot(netTrade[(np.logical_or(netTrade['pctBought'] < 200, netTrade['pctBought'] > 800))]['pctBought'])
#axs[2].plot(netTrade[(np.logical_or(netTrade['netTrade'] < -25, netTrade['netTrade'] > 25))]['netTrade'])

#axs[1].plot(netTrade.nsmallest(5, 'pctBought')['pctBought'], 'ro')
#axs[1].plot(netTrade['grossTrade'], 'ro', markersize=1.0)

#plt.title('Drawdown for next ' + str(FMA*5) + ' minutes')
#plt.gca().xaxis.set_major_locator(plt.MaxNLocator(28))

#plt.plot(BBO.loc[minPctIndex]['bid'], 'ro')
#plt.plot(BBO.loc[maxPctIndex]['bid'], 'kx')
#plt.plot(BBO.loc[minGrossIndex]['bid'], 'mx')
#plt.plot(BBO.loc[maxGrossIndex]['bid'], 'go')

#axs[0].plot([VWOrders.index[0], VWOrders.index[-1]], [np.max(VWOrders['VWBids'] - BBO['bid']), np.max(VWOrders['VWBids'] - BBO['bid'])], 'r--')
#axs[0].plot([VWOrders.index[0], VWOrders.index[-1]], [np.mean(VWOrders['VWBids'] - BBO['bid']), np.mean(VWOrders['VWBids'] - BBO['bid'])], 'r--')
#axs[0].plot([VWOrders.index[0], VWOrders.index[-1]], [np.min(VWOrders['VWAsks'] - BBO['bid']), np.min(VWOrders['VWAsks'] - BBO['bid'])], 'r--')
#axs[0].plot([VWOrders.index[0], VWOrders.index[-1]], [np.mean(VWOrders['VWAsks'] - BBO['bid']), np.mean(VWOrders['VWAsks'] - BBO['bid'])], 'r--')