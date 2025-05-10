from binance.client import Client
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
import requests

baseEndpoint = 'https://api.binance.com'
btc_usd_ticker = requests.get(baseEndpoint + '/api/v3/depth', params=dict(symbol="BTCUSDT", limit=5000)).json()
t = time.time()
currentTime = time.strftime('%H-%M-%S', time.localtime(t))
currentDate = time.strftime('%Y-%m-%d', time.localtime(t))

totalBids = 0
weightedPriceBids = 0
for bid in btc_usd_ticker['bids']: # actually isnt much slower than pandas, ~.001s
    totalBids += float(bid[1])
    weightedPriceBids += float(bid[0]) * float(bid[1])

VWBids = weightedPriceBids / totalBids
print(VWBids)

totalAsks = 0
weightedPriceAsks = 0
for ask in btc_usd_ticker['asks']:
    totalAsks += float(ask[1])
    weightedPriceAsks += float(ask[0]) * float(ask[1])

VWAsks = weightedPriceAsks / totalAsks
print(VWAsks)

DB_NAME = 'VolumeWeightedOrderbook'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DB_NAME)
recentFilter = 660  # 11 minutes in UNix time
trades = table.query(
    KeyConditionExpression=Key('hash').eq("1")
                           & Key('unixtime').lt(str(time.time() - recentFilter)),
)
print(trades)
for item in trades['Items']:

    table.delete_item(
        Key={
            'hash': "1",
            'unixtime': item['unixtime']
        }
    )