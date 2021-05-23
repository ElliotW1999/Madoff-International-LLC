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

cur.execute("SELECT * FROM minuteSnapshots Where asks_price IS NOT NULL")
asks = cur.fetchall()
asks = pd.DataFrame(asks, columns=["time", "bids price", "bids vol", "price", "asks"]).dropna(axis=1)
asks['price (x100)'] = [int(str(x)[:3]) for x in asks['price']]     # rounds to nearest hundred

# separate by time, then group by price (x100), then combine
times = asks['time'].tolist()
times = sorted(list(set(times)))
i = 0
for time in times:
    times[i] = asks[asks['time'] == time]
    times[i] = times[i].rename(columns={'asks' : time[:-10]})
    times[i] = times[i].groupby('price (x100)')
    i = i+1

asksVisualised = pd.concat([x.sum() for x in times], axis=1, join='outer')
asksVisualised = asksVisualised.drop('price', axis=1)
asksVisualised = asksVisualised.iloc[::-1] # flip vertically for visualisation

# --------- repeat for bids -----------
cur.execute("SELECT * FROM minuteSnapshots Where bids_price IS NOT NULL")
bids = cur.fetchall()
bids = pd.DataFrame(bids, columns=["time", "price", "bids", "asks price", "asks vol"]).dropna(axis=1)
bids['price (x100)'] = [int(str(x)[:3]) for x in bids['price']]     # rounds to nearest hundred

# separate by time, then group by price (x100), then combine
times = bids['time'].tolist()
times = sorted(list(set(times)))
i = 0
for time in times:
    times[i] = bids[bids['time'] == time]
    times[i] = times[i].rename(columns={'bids' : time[:-10]})
    times[i] = times[i].groupby('price (x100)')
    i = i+1

bidsVisualised = pd.concat([x.sum() for x in times], axis=1, join='outer')
bidsVisualised = bidsVisualised.drop('price', axis=1)
bidsVisualised = bidsVisualised.iloc[::-1] # flip vertically for visualisation

fig, axs = plt.subplots(nrows=2, figsize=(20, 20))

# may be able to have both on one plot?
#axs = sns.heatmap(pd.concat([asksVisualised, bidsVisualised], axis=0, join='outer'), cmap="Reds", annot=False)
sns.heatmap(asksVisualised, ax=axs[0], cmap="Reds", annot=False)

sns.heatmap(bidsVisualised, ax=axs[1], cmap="Greens", annot=False)

plt.yticks(rotation=0)
plt.show()