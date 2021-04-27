import asyncio
from datetime import datetime
from copra.websocket import Channel, Client, FEED_URL
import os
import sqlite3
from sqlite3 import Error, Cursor


class Ticker(Client):
    def __init__(self, loop, channels, feed_url=FEED_URL,
                 auth=False, key='', secret='', passphrase='',
                 auto_connect=True, auto_reconnect=True,
                 name='WebSocket Client'):
        super().__init__(loop, channels, feed_url, auth, key, secret, passphrase, auto_connect, auto_reconnect, name)

        db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/orderbook.db"
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        self.cur = conn.cursor()

    def initDatabase(self, cursor):
        pass

    def on_message(self, message):
        if message['type'] == 'l2update':
            print(message['product_id'])
            print(message['changes'])
            print(datetime.strptime(message['time'], '%Y-%m-%dT%H:%M:%S.%fZ') )
        elif message['type'] == 'snapshot':
            print(message['product_id'])
            print(message['bids'])
            print(message['asks'])


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
