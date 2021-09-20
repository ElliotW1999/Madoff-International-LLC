from datetime import datetime, timedelta
import requests
import boto3
import csv
import json

def main(event, context):   
    
    baseEndpoint = 'https://api.binance.com'
    recent_trades = requests.get(baseEndpoint + '/api/v3/trades', params=dict(symbol="BTCUSDT", limit=1000)).json()
    prices = []
    qtys = []
    isBuyerMaker = []
    times = []
    for trade in recent_trades:
        prices.append(trade['price'])
        qtys.append(trade['qty'])
        isBuyerMaker.append(trade['isBuyerMaker'])
        times.append(trade['time'])
    
    
    DB_NAME = 'recenttradesBinance'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DB_NAME)
    key = datetime.now().strftime("%m-%d-%Y,%H_%M_%S")
    
    table.put_item(Item={
        'timestamp': key,
        'time': times,
        'price': prices,
        'size': qtys,
        'isBuyerMaker': isBuyerMaker
    })