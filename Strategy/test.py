import os
import sqlite3
from sqlite3 import Error
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from matplotlib import cm

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
FMA = 144
indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=FMA)
BBO['avgChange_'+str(FMA)] = BBO['logBid'].rolling(window=indexer).sum()
BBO['vol'] = BBO['bidPctChange'].rolling(window=indexer).std()

VWOrders = """Select * from orderbookFeatures order by date"""
cur.execute(VWOrders)
VWOrders = cur.fetchall()
VWOrders = pd.DataFrame(VWOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])
BBO['netVW'] = (VWOrders['VWAsks'] - BBO['bid']) + (VWOrders['VWBids'] - BBO['bid'])
BBO.dropna(inplace=True)
pctChangeFMAScaled = (BBO['avgChange_'+str(FMA)] - BBO['avgChange_'+str(FMA)].min() )/\
                     (BBO['avgChange_'+str(FMA)].max() - BBO['avgChange_'+str(FMA)].min() ) # range 0-1

threshold = 1000

result = stats.linregress(BBO[ (BBO['netVW'] < -1*threshold) | (BBO['netVW'] > threshold)]['avgChange_'+str(FMA)],
                BBO[ (BBO['netVW'] < -1*threshold) | (BBO['netVW'] > threshold)]['netVW'])
print(result)
print(f"R-squared: {result.rvalue**2:.6f}")

plt.figure() # Plot
plt.scatter(BBO.index, BBO['bid'],
            c=cm.RdBu( pctChangeFMAScaled), s=2.5, edgecolor='none') #'r--'
plt.scatter(BBO[ (BBO['netVW'] < -1*threshold)]['bid'].index,
                BBO[ (BBO['netVW'] < -1*threshold)]['bid'], c='red', marker='x')
plt.scatter(BBO[ (BBO['netVW'] > threshold)]['bid'].index,
                BBO[ (BBO['netVW'] > threshold)]['bid'], c='green', marker='x')
plt.figure()
plt.plot(BBO['bid'], linewidth=0.25)
plt.scatter(BBO[ (BBO['netVW'] < -1*threshold)]['bid'].index,
                BBO[ (BBO['netVW'] < -1*threshold)]['bid'], c='red', marker='x')
plt.scatter(BBO[ (BBO['netVW'] > threshold)]['bid'].index,
                BBO[ (BBO['netVW'] > threshold)]['bid'], c='green', marker='x')

plt.figure() # Plot scatter of 12 hr changes only when net VW > or < threshold
plt.scatter(BBO[ (BBO['netVW'] < -1*threshold) | (BBO['netVW'] > threshold)]['avgChange_'+str(FMA)],
                BBO[ (BBO['netVW'] < -1*threshold) | (BBO['netVW'] > threshold)]['netVW'])

plt.figure() # Plot dist of 12hr changes following net VW > or < threshold
sns.distplot(BBO[(BBO['netVW'] < -1*threshold)]['avgChange_'+str(FMA)], label='less than -'+str(threshold),
                                            bins=500, hist=False)
sns.distplot(BBO[(BBO['netVW'] > threshold)]['avgChange_'+str(FMA)], label='more than '+str(threshold),
                                            bins=500, hist=False)
sns.distplot(BBO['avgChange_'+str(FMA)], label='total',
                                            bins=500, hist=False)
plt.legend()



fig, axs = plt.subplots(2)
axs[0].plot(BBO['vol'])
axs[1].plot(VWOrders['VWBids'] - BBO['bid'])
axs[1].plot(VWOrders['VWAsks'] - BBO['bid'])
axs[1].axhline(y=0, color='g', linestyle='--')

plt.figure() # Plot dist of 12hr changes following net VW > or < threshold
sns.distplot(BBO[ (VWOrders['VWBids'] - BBO['bid']) < -1.5*threshold]['vol'], label='less than -'+str(threshold),
                                            bins=500, hist=False)
sns.distplot(BBO[ (VWOrders['VWAsks'] - BBO['bid']) > 1.5*threshold]['vol'], label='more than '+str(threshold),
                                            bins=500, hist=False)
sns.distplot(BBO['vol'], label='total',
                                            bins=500, hist=False)
plt.legend()

thresholdVol = []
for i in range(0,50):
    thresholdVol.append((np.mean(BBO[ (VWOrders['VWBids'] - BBO['bid']) < -i*threshold*0.06]['vol']) +
                        np.mean(BBO[ (VWOrders['VWAsks'] - BBO['bid']) > i*threshold*0.06]['vol'])) / 2)
plt.figure()
plt.plot(thresholdVol)


plt.show()
