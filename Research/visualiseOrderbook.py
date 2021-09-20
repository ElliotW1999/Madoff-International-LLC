import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import datetime as datetime

db_file = os.path.dirname(os.path.dirname( __file__ ))+"/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

cur.execute("SELECT * FROM asks Where date between '08-20-2021' and '08-22-2021'")
asks = cur.fetchall()
print(asks)
asks = pd.DataFrame(asks, columns=["bids price", "bids vol", "asks price", "asks vol"]).dropna(axis=1)
asks.set_index("asks price", drop=True, inplace=True)
cur.execute("SELECT * FROM updates limit 100")


times = []
for response in data:
    for item in response['Items']:
        times.append(item['timestamp'])

bids = [None] * len(times)
asks = [None] * len(times)
BBO = pd.DataFrame(columns=['time', 'ask', 'bid'])

i = 0
print(sorted(times))
for time in sorted(times):  # this is gross
    for response in data:
        for item in response['Items']:
            if time == item['timestamp']:
                asks[i] = pd.DataFrame(data=item['asks'], columns=['price', 'vol'], dtype='float')
                asks[i] = asks[i][:50]
                asks[i]['price'] = asks[i]['price'] - asks[i]['price'][0]
                asks[i]['price (x100)'] = [int( ( str( int(x) ).zfill(5) )[:3] ) for x in asks[i]['price']]
                print(asks[i])
                asks[i] = asks[i].rename(columns={'vol' : ' '}) # only need bottom of axis labelled
                asks[i] = asks[i].groupby('price (x100)')

                bids[i] = pd.DataFrame(data=item['bids'], columns=['price', 'vol'], dtype='float')
                bids[i] = bids[i][:50]
                bids[i]['price'] = bids[i]['price'] - bids[i]['price'][0]
                bids[i]['price (x100)'] = [int( ( str( abs(int(x)) ).zfill(5) )[:3] ) for x in bids[i]['price']] #int((str(int(x)).zfill(6))[:3])
                bids[i] = bids[i].rename(columns={'vol' : time[:-3]})
                bids[i] = bids[i].groupby('price (x100)')
                BBO.loc[i] = [time, float(item['asks'][0][0]), float(item['bids'][0][0])]

                i += 1

asksVisualised = pd.concat([x.sum() for x in asks], axis=1, join='outer')
asksVisualised = asksVisualised.drop('price', axis=1)
#asksVisualised = asksVisualised[1:]
asksVisualised = asksVisualised.diff(axis=1)
asksVisualised = asksVisualised.mask(abs(asksVisualised) < 1, 0)
asksVisualised.replace(0, np.nan, inplace=True)
asksVisualised = asksVisualised.iloc[::-1] # flip vertically for visualisation

print(BBO)

bidsVisualised = pd.concat([x.sum() for x in bids], axis=1, join='outer')
bidsVisualised = bidsVisualised.drop('price', axis=1)
#bidsVisualised = bidsVisualised[1:]
bidsVisualised = bidsVisualised.diff(axis=1)
bidsVisualised = bidsVisualised.mask(abs(bidsVisualised) < 1, 0)
bidsVisualised.replace(0, np.nan, inplace=True)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(asksVisualised)
    print(bidsVisualised)

fig, axs = plt.subplots(nrows=2, figsize=(20, 20))

# may be able to have both on one plot?
#axs = sns.heatmap(pd.concat([asksVisualised, bidsVisualised], axis=0, join='outer'), cmap="Reds", annot=False)
sns.heatmap(asksVisualised, ax=axs[0], cmap="Reds", annot=True, fmt=".0f",
            annot_kws={'rotation': 45, 'color': 'blue'}, robust=True)
BBO.plot(x='time', y=['ask', 'bid'])
sns.heatmap(bidsVisualised, ax=axs[1], cmap="Greens", annot=True, fmt=".0f",
            annot_kws={'rotation': 45, 'color': 'blue'}, robust=True)

plt.show()
