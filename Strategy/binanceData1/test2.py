# Using VWAP as entry and exit points
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

BBO = """Select * from BBO where date like "%2021" """
cur.execute(BBO)
BBO = cur.fetchall()
BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bid', 'ask'])

VWOrders = """Select * from orderbookFeatures where date like "%2021" order by date """
cur.execute(VWOrders)
VWOrders = cur.fetchall()
VWOrders = pd.DataFrame(VWOrders, columns=['date', 'time', 'VWBids', 'VWAsks'])

bids = BBO[ (BBO['ask'] > VWOrders['VWAsks'].shift(1)) ] #buys
asks = BBO[ (BBO['bid'] < VWOrders['VWBids'].shift(1)) ] #sells

# buy after 12 hrs
rebuy = asks.copy(deep=False)
#trades = pd.concat([bids, BBO.iloc[asks.index+144]], axis=0, sort=True) #TODO: check if sell in past 143 steps
trades = bids

trades = trades.append(BBO.iloc[0])
trades['trade'] = 1
asks = asks.copy(deep=False)
asks = asks.append(BBO.iloc[-1])
asks['trade'] = 0
trades = pd.concat([trades, asks], axis=0, sort=True)
trades.sort_index(axis=0, inplace=True)
trades['index'] = trades.index
trades['prev_trade'] = trades['trade'].shift()
trades['groups'] = (trades['trade'] != trades['prev_trade']).cumsum()
trades = trades.groupby('groups').first()
trades.set_index('index', drop=True, inplace=True)
trades.drop(['prev_trade'], axis=1, inplace=True)
trades.sort_index(axis=0, inplace=True)
trades['equity'] = 10000
print(trades)

index = trades.index.values
prev_index = index[0]
mylist = np.array((prev_index, 10000))
mylist = np.vstack((mylist, np.array((prev_index, 10000))))
# Calculating change in capital
for index in trades.index[1:]:
    if trades.loc[index]['trade'] == 0:
        mylist = np.vstack((mylist, np.array((index, mylist[-1][-1] * 1 * (trades.loc[index]['bid']/trades.loc[prev_index]['bid'])))))
    else:
        mylist = np.vstack((mylist, np.array((index, mylist[-1][-1] * 1)))) # * fees
    prev_index = index

mylist = pd.DataFrame(mylist, columns=['index', 'equity'])
mylist.set_index('index', inplace=True, drop=True)
mylist = mylist.iloc[1:, :] #remove repeated position
print(mylist)

bidDeltas = """Select * from bidDeltas"""
cur.execute(bidDeltas)
bidDeltas = cur.fetchall()
bidDeltas = pd.DataFrame(bidDeltas, columns=['date', 'time', 'bid', 'logBid', 'bidPctChange'])

buyAndHold_LogReturn = np.sum(bidDeltas['logBid'])
buyAndHold_Sharpe = bidDeltas['logBid'].mean()/bidDeltas['logBid'].std()
buyAndHold_SharpeAnnualized = buyAndHold_Sharpe * np.sqrt(105120) / np.sqrt(len(bidDeltas))

#drawdown
print(len(bidDeltas))
print(buyAndHold_SharpeAnnualized)


mylistNew = mylist.iloc[::2, :] #TODO take another look at this
mylistNew['log'] = np.log(mylistNew['equity']/mylistNew['equity'].shift())
strat_logReturn = np.sum(mylistNew['log'])
strat_Sharpe = mylistNew['log'].mean()/mylistNew['log'].std()
strat_SharpeAnnualized = strat_Sharpe * np.sqrt(105120) / np.sqrt(len(bidDeltas))
print(strat_SharpeAnnualized)

df = {'price': mylist.iloc[::2, :]['equity']}  #TODO take another look at this
returns = pd.DataFrame(data=df, columns=['price'])
returns['cumMax'] = returns['price'].cummax()
returns['drawdown'] = returns['price'] - returns['cumMax'] #TODO finish calculating max drawdown
print(returns)

df = {'price': mylist['equity']}
kelly = pd.DataFrame(data=df, columns=['price'])
kelly['returns'] = kelly['price'] - kelly['price'].shift()
wins = kelly[kelly['returns'] > 0]['returns']
losses = kelly[kelly['returns'] < 0]['returns']
print(kelly)
print(wins)
print(losses)
winProb = len(wins)/ (len(wins) + len(losses))
winRatio = wins.mean() / abs(losses.mean())
kellyCriterion = winProb - ((1-winProb)/winRatio)
print(kellyCriterion)

BBO['trade'] = trades['trade']
BBO['trade'] = BBO['trade'].interpolate(method='pad')
BBO['pctChange'] = BBO['bid'].shift(periods=-1) / BBO['bid']
BBO['equity'] = BBO[BBO['trade'] == 1]['pctChange'].cumprod()
BBO['equity'] = 10000 * BBO['equity']
BBO['equity'] = BBO['equity'].interpolate(method='pad')
print(BBO)

plt.figure()
plt.plot(BBO['equity'] - (BBO['bid']/BBO['bid'][0]*10000), 'r', linestyle='--', linewidth=.25, label='Strategy equity')


plt.figure()
plt.plot(BBO['equity'], 'r', linestyle='--', linewidth=.25, label='Strategy equity')
plt.plot(BBO['bid']/BBO['bid'][0]*10000, 'g', linestyle='--', linewidth=.25, label='Buy-and-hold equity')

plt.figure()
plt.plot(returns['drawdown'])
plt.plot(returns['price'] - 10000)


fig, axs = plt.subplots(2)
axs[0].plot(BBO['bid'], 'g', linestyle='--', linewidth=.25)
axs[0].scatter( trades[trades['trade'] == 0].index,
               trades[trades['trade'] == 0]['bid'], marker='x', c='red')
axs[0].scatter( trades[trades['trade'] == 1].index,
               trades[trades['trade'] == 1]['bid'], marker='x', c='blue')
#axs[0].scatter( BBO.iloc[asks.index+144].index,
#                BBO.iloc[asks.index+144]['bid'], marker='x', c='blue')
axs[1].plot(mylist)

plt.figure()
plt.plot(BBO['bid'], 'g', linestyle='--', linewidth=.25)
plt.scatter( asks.index,
               asks['bid'], marker='x', c='red')
#plt.scatter( BBO.iloc[rebuy.index+144].index, BBO.iloc[rebuy.index+144]['bid'], marker='x', c='blue')
plt.scatter( bids.index,
               bids['bid'], marker='x', c='blue')

fig,axs = plt.subplots(2)
#plt.figure()
axs[0].plot(mylist, label='Strategy Equity')
axs[0].plot(BBO['bid']/BBO['bid'][0]*10000, 'g', linestyle='--', linewidth=.25, label='Buy-and-hold equity')
#axs[0].title('Performace of strategy compared to underlying asset')
axs[0].legend()

axs[1].plot(BBO['trade'])

plt.show()
