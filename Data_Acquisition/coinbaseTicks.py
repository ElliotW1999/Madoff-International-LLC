import asyncio
from datetime import datetime
from copra.websocket import Channel, Client, FEED_URL
import os
import sqlite3
from sqlite3 import Error


class Ticker(Client):
    def __init__(self, loop, channels, feed_url=FEED_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, auto_reconnect=True,
                 name='WebSocket Client'):
        super().__init__(loop, channels, feed_url, auth, key, secret, passphrase, auto_connect, auto_reconnect, name)

        db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/orderbook.db"
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        self.cur = self.conn.cursor()

    def on_message(self, message):
        if message['type'] == 'l2update':
            timestamp = datetime.strptime(message['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            for change in message['changes']:
                sqlite_insert_with_param = """INSERT INTO updates (time, side, price, size) VALUES (?, ?, ?, ?);"""
                data_tuple = (timestamp, change[0], change[1], change[2])
                self.cur.execute(sqlite_insert_with_param, data_tuple)
            self.conn.commit()

        elif message['type'] == 'snapshot':
            for bid in message['bids']:
                sqlite_insert_with_param = """INSERT INTO snapshot (bids_price, bids_vol) VALUES (?, ?);"""
                data_tuple = (bid[0], bid[1])
                self.cur.execute(sqlite_insert_with_param, data_tuple)

            for ask in message['asks']:
                sqlite_insert_with_param = """INSERT INTO snapshot (asks_price, asks_vol) VALUES (?, ?);"""
                data_tuple = (ask[0], ask[1])
                self.cur.execute(sqlite_insert_with_param, data_tuple)

            self.conn.commit()


loop = asyncio.get_event_loop()

ws = Ticker(loop, Channel('level2', 'BTC-USD'))

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(ws.close())
    loop.close()

#from coinbase import CoinbaseAccount
#print(CoinbaseAccount().exchange_rates['usd_to_btc'])
#account = CoinbaseAccount(oauth2_credentials=JSON_OAUTH2_TOKEN)
#transaction = account.send('recipient@example.com', 1.0)
#print(transaction.status)
#https://github.com/sibblegp/coinbase_python

#from coinbase.wallet.client import Client
#api_key = "8427a6e4eeae902a750a493cfa9b9c13"
#api_secret = "PLFlHcvUi6Pc9/LRm0tMT6EvwiEntK0VIv9riDWbhMUBXDnr0FHFzNxI9ZyJG16WTDDK/u66pAu4/jmmiaaZzw=="
#client = Client(api_key, api_secret)

#currencies = client.get_currencies()
#print(currencies)


#wss://ws-feed-public.sandbox.pro.coinbase.com
# to do it manually: https://docs.pro.coinbase.com/?python#signing-a-message
