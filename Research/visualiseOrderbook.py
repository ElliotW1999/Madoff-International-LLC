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
updates = cur.fetchall()
#updates = pd.DataFrame(updates)
#print(updates)
for update in updates:
    if update[1] == "sell":
        asks[update[0]] = asks.iloc[:,-1:]
        if update[3] == 0:
            asks.loc[update[2], update[0]] = 0.0
        else:
            try:
                asks.loc[update[2], update[0]] += update[3]
            except:
                asks.loc[update[2], update[0]] = update[3]

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

plt.show()
