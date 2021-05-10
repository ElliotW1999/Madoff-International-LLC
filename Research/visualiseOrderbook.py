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

cur.execute("SELECT * FROM snapshot Where asks_price IS NOT NULL limit 3200")
asks = cur.fetchall()
asks = pd.DataFrame(asks, columns=["bids price", "bids vol", "asks price", "asks vol"]).dropna(axis=1)
asks.set_index("asks price", drop=True, inplace=True)
print(asks.index[0])
asks['pct diff'] = [round(100*(round((x/asks.index[0]), 3)-1),2) for x in asks.index]
#asks['pct diff'] = [(round((x/asks.index[0]), 4)) for x in asks.index]
print(asks)
grouped = asks.groupby('pct diff')
print(grouped.sum())

cur.execute("SELECT * FROM snapshot Where bids_price IS NOT NULL limit 5000")  # ~15% pct diff from best bid
bids = cur.fetchall()
bids = pd.DataFrame(bids).dropna(axis=1)
#print(bids)
fig, ax = plt.subplots(figsize=(16, 16))
ax = sns.heatmap(grouped.sum(), annot=True)

#cur.execute("SELECT * FROM snapshot Where asks_price IS NOT NULL Limit 5000")
#asks = cur.fetchall()
#asks = pd.DataFrame(asks, columns=["bids price", "bids vol", "asks price", "asks vol"]).dropna(axis=1)
#plt.plot(asks["asks vol"], asks["asks price"], "crimson", label="asks")
#plt.plot(bids[1], bids[0], "limegreen", label="bids")
#plt.legend()

plt.show()
