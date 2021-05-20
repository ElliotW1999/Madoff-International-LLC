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
asks = pd.DataFrame(asks, columns=["time", "bids price", "bids vol", "price", "vol"]).dropna(axis=1)
asks['bucket'] = [int(str(x)[:3]) for x in asks['price']]
print(asks)
# TODO: separate by time, then group by bucket, then combine
times = asks['time'].tolist()
times = sorted(list(set(times)))
print(times)
# TODO: make these not hardcoded
maxbucket = asks[asks['time'] == "2021-05-19 18:48:26.295298"].ind
minbucket = 0
for time in times:
    print(time)


timeA = asks[asks['time'] == "2021-05-19 18:48:26.295298"]
timeB = asks[asks['time'] == "2021-05-19 20:03:25.289879"]
timeAgrouped = timeA.groupby('bucket')
timeBgrouped = timeB.groupby('bucket')

print(timeAgrouped.sum())
print(timeBgrouped.sum())
test = pd.concat([timeAgrouped.sum(), timeBgrouped.sum()], axis=1, join='outer')
test = test.drop('price', axis=1)
print(test)

asks.set_index('bucket', drop=True)
asks = asks.drop('price', axis=1)
#bidsGrouped = asks.groupby('bucket')
fig, ax = plt.subplots(figsize=(16, 16))
ax = sns.heatmap(test, cmap="Reds", annot=True)
plt.yticks(rotation=0)
plt.show()