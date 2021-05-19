import asyncio
from datetime import datetime
from copra.rest import Client, APIRequestError
import os
import sqlite3
from sqlite3 import Error
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

loop = asyncio.get_event_loop()

async def run():

    async with Client(loop, auth=False) as client:
        # Get the last price of BTC-USD
        btc_usd_ticker = await client.order_book('BTC-USD', 3)
        bids = pd.DataFrame(btc_usd_ticker['bids'], columns=['price', 'volume', 'tradeID'], dtype=float)
        bids['diff'] = (bids['price'] - bids.loc[0]['price'])/ bids.loc[0]['price']
        bids = bids.drop('tradeID', axis=1)
        bids = bids[bids['diff'] > -.25]
        bids = bids.drop('diff', axis=1)

        asks = pd.DataFrame(btc_usd_ticker['asks'], columns=['price', 'volume', 'tradeID'], dtype=float)
        asks['diff'] = (asks['price'] - asks.loc[0]['price']) / asks.loc[0]['price']
        asks = asks.drop('tradeID', axis=1)
        asks = asks[asks['diff'] < .25]
        asks = asks.drop('diff', axis=1)

        # Visualise
        #asks['bucket'] = [int(str(x)[:3]) for x in asks['price']]
        #asks.set_index('bucket', drop=True)
        #asks = asks.drop('price', axis=1)
        #bidsGrouped = asks.groupby('bucket')
        #fig, ax = plt.subplots(figsize=(16, 16))
        #ax = sns.heatmap(bidsGrouped.sum(), cmap="Reds", annot=True)
        #plt.yticks(rotation=0)
        #plt.show()
        # end Visualise

        currentTime = datetime.now()
        #TODO: can use pandas to save in batch

        db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/orderbook.db"
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        cur = conn.cursor()

        for index, row in bids.iterrows():
            sqlite_insert_with_param = """INSERT INTO minuteSnapshots (time, bids_price, bids_vol) VALUES (?, ?, ?);"""
            data_tuple = (currentTime, row['price'], row['volume'])
            cur.execute(sqlite_insert_with_param, data_tuple)

        for index, row in asks.iterrows():
            sqlite_insert_with_param = """INSERT INTO minuteSnapshots (time, asks_price, asks_vol) VALUES (?, ?, ?);"""
            data_tuple = (currentTime, row['price'], row['volume'])
            cur.execute(sqlite_insert_with_param, data_tuple)

        conn.commit()

        sys.exit()

loop.run_until_complete(run())

loop.close()