import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

db_file = os.path.dirname(os.path.dirname( __file__ ))+"/Data/orderbook.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

cur.execute("SELECT * FROM snapshot Where asks_price IS NOT NULL limit 2000")
asks = cur.fetchall()
asks = pd.DataFrame(asks, columns=["bids price", "bids vol", "asks price", "asks vol"]).dropna(axis=1)
asks.set_index("asks price", drop=True, inplace=True)
cur.execute("SELECT * FROM updates limit 100")

#TODO : group updates by minute
# currently pretty slow, might need vectorization

updates = cur.fetchall()
updates = pd.DataFrame(updates)
updates[updates.columns.values[0]] = updates[updates.columns.values[0]].apply(lambda x: str(x)[:-7] )
updates = updates.set_index(updates.columns[0])
sellUpdates = updates[updates[1] == "sell"]
sellUpdates = sellUpdates.drop(sellUpdates.columns.values[0], axis=1)
#TODO: repeat for buys
buyUpdates = updates[updates[1] == "buy"]

#minutes = updates.index.unique()
minute = "2021-04-28 05:24:26"
#for minute in minutes:
# add column for minute
asks[minute] = asks.iloc[:, -1:]
# add rows for new prices

addedSells = sellUpdates[(sellUpdates.index == minute) & (sellUpdates[3] != 0)].reset_index(drop=True)

newAddedSells = addedSells[~addedSells[2].isin(asks.index)]
modAddedSells = addedSells[addedSells[2].isin(asks.index)]
#print(modAddedSells[3].reset_index(drop=True))
#print(pd.Series(asks.index))
#asks.loc[modAddedSells[2], minute] += modAddedSellsGrouped.sum()
asks.loc[modAddedSells[2], minute] += modAddedSells[3].values
#print(asks.loc[modAddedSells[2], minute])
#print(asks.loc[modAddedSells[2], minute] + modAddedSells[3].values)

#print(newAddedSells)
#print(updates[(updates.index == minute) & (updates[3] != 0)])
#print(updates[(updates.index == minute) & (updates[3] == 0)][2])
#print(asks[asks.index.isin(priceLevels)])


# add to existing prices
# deduct cleared prices


currentTime = updates[0][0][0:-10]              # initial time in minutes
asks[updates[0][0][0:-10]] = asks.iloc[:,-1:]   # duplicates initial snapshot for first minute
for update in updates:
    #print(update[0][0:-10])
    #print(currentTime)
    if (update[0][0:-10] != currentTime):       # if new minute, create a new column
        currentTime = update[0][0:-7]
        asks[currentTime] = asks.iloc[:,-1:]
    if update[1] == "sell":                     # for changes to sell orders
        if update[3] == 0:                      # if price level is cleared
            asks.loc[update[2], update[0]] = 0.0
        else:
            try:                                # update exisitng price level
                asks.loc[update[2], update[0]] += update[3]
            except:                             # if level does not exist, create new level
                asks.loc[update[2], update[0]] = update[3]
    # TODO: else if "buy"

buckets = asks.copy().fillna(0)
buckets['price (00) (floor)'] = [int(str(x)[:3]) for x in asks.index]
buckets.set_index('price (00) (floor)', drop=True)
#print(buckets)
#buckets = buckets.applymap(lambda x: int(str(x)[:3]) )
#print(asks.columns)
#print(asks)
#print(asks.applymap(lambda x: int(str(x)[:3]) ) )
#print(buckets)

#todo: select resolution of x and y axis
asksGrouped = buckets.groupby('price (00) (floor)')
#print(asksGrouped.sum())

cur.execute("SELECT * FROM snapshot Where bids_price IS NOT NULL limit 5000")  # ~15% pct diff from best bid
bids = cur.fetchall()
bids = pd.DataFrame(bids).dropna(axis=1)
#print(bids)
fig, ax = plt.subplots(figsize=(16, 16))
ax = sns.heatmap(asksGrouped.sum(), cmap="Reds", annot=True)
plt.yticks(rotation=0)


#cur.execute("SELECT * FROM snapshot Where asks_price IS NOT NULL Limit 5000")
#asks = cur.fetchall()
#asks = pd.DataFrame(asks, columns=["bids price", "bids vol", "asks price", "asks vol"]).dropna(axis=1)
#plt.plot(asks["asks vol"], asks["asks price"], "crimson", label="asks")
#plt.plot(bids[1], bids[0], "limegreen", label="bids")
#plt.legend()

#plt.show()




#print(list(modAddedSells[3]))
#print(pd.Series(asks.index))
#asks.loc[modAddedSells[2], minute] += modAddedSellsGrouped.sum()
#asks.loc[modAddedSells[2], minute] += list(modAddedSells[3])
#print(asks.loc[modAddedSells[2], minute])
#print(asks)
#print(newAddedSells)
#print(updates[(updates.index == minute) & (updates[3] != 0)])
#print(updates[(updates.index == minute) & (updates[3] == 0)][2])
#print(asks[asks.index.isin(priceLevels)])


