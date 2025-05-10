import requests
from binance.client import Client
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr

def handler(event, context):
    client = Client(os.environ['api_key'],
                    os.environ['api_secret'])
    client.API_URL = 'https://testnet.binance.vision/api'
    btc_balance = client.get_asset_balance(asset='BTC')
    usdt_balance = client.get_asset_balance(asset='USDT')
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")

    # TODO: be able to sell LTC/ something else
    # TODO: potentially check last trade to make sure actual qty = orig qty

    # START get most recent VWs
    DB_NAME = 'VolumeWeightedOrderbook'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DB_NAME)
    recentFilter = 360  # 6 minutes in UNix time
    indicators = table.query(
        KeyConditionExpression=Key('hash').eq("1") & Key('unixtime').gt(str(time.time() - recentFilter)),
    )
    bidIndicators = []
    askIndicators = []
    for item in indicators['Items']:
        bidIndicators.append(float(item['VWBids']))
        askIndicators.append(float(item['VWAsks']))
    # END get most recent VWs
    tradeMade = False

    # START place orders
    if float(btc_balance['free']) > 1.0:
        for bidIndicator in bidIndicators:
            if bidIndicator > float(btc_price['price']):
                # START trade function
                origQty = float(btc_balance['free']) - 1.0
                actualQty = 0
                while actualQty < origQty - 0.00001:
                    market_sell = client.order_market_sell(symbol='BTCUSDT', quantity=float(round(origQty - actualQty, 6)))
                    if market_sell['status'] == 'EXPIRED':
                        break
                    actualQty += float(market_sell['executedQty'])
                    time.sleep(0.5)

                mywallet = client.get_account()
                tradeTime = time.time()
                TradesDB = 'trades'
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(TradesDB)
                table.put_item(Item={
                    'side': market_sell['side'],
                    'tradeTime': str(tradeTime),  # 'tradeTime': str(market_buy['transactTime']),
                    'price': str(float(market_sell['cummulativeQuoteQty'])/ float(market_sell['executedQty'])),
                    'origQty': str(market_sell['origQty']),
                    'executedQty': str(actualQty),
                    'status': str(market_sell['status']),
                    'btcBalance': str(mywallet['balances'][1]['free']),  # btc, do this when trades are complete
                    'USDTBalance': str(mywallet['balances'][-2]['free'])  # usdt
                })
                # END trade function
                tradeMade = True
                break
    else:
        for askIndicator in askIndicators:
            if askIndicator < float(btc_price['price']):
                # START trade function
                origQty = (float(usdt_balance['free']) - 5000.0) / float(btc_price['price'])
                actualQty = 0
                while actualQty < origQty - 0.00001:
                    market_buy = client.order_market_buy(symbol='BTCUSDT', quantity=float(round(origQty - actualQty, 6)))
                    if market_buy['status'] == 'EXPIRED':
                        break
                    actualQty += float(market_buy['executedQty'])
                    time.sleep(0.5)

                mywallet = client.get_account()
                tradeTime = time.time()
                TradesDB = 'trades'
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(TradesDB)
                table.put_item(Item={
                    'side': market_buy['side'],
                    'tradeTime': str(tradeTime),  # 'tradeTime': str(market_buy['transactTime']),
                    'price': str(float(market_buy['cummulativeQuoteQty'])/ float(market_buy['executedQty'])),
                    'origQty': str(market_buy['origQty']),
                    'executedQty': str(actualQty),
                    'status': str(market_buy['status']),
                    'btcBalance': str(mywallet['balances'][1]['free']),  # btc, do this when trades are complete
                    'USDTBalance': str(mywallet['balances'][-2]['free'])  # usdt
                })
                # END trade function
                tradeMade = True
                break

    btc_balance = client.get_asset_balance(asset='BTC')
    usdt_balance = client.get_asset_balance(asset='USDT')

    # START get positions before reset
    if (float(btc_balance['free']) == 1.0 and float(usdt_balance['free']) == 10000.0):
        print('test')
        DB_NAME = 'trades'
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DB_NAME)
        recentFilter = 360  # 6 minutes in UNix time
        lastTrade = table.query(
            KeyConditionExpression=Key('side').eq('None') & Key('tradeTime').gt(str(time.time() - recentFilter)),
        )
        if lastTrade['Count'] == 0:
            lastTrade = table.query(
                KeyConditionExpression=Key('side').eq('BUY') & Key('tradeTime').gt(str(time.time() - recentFilter)),
            )
        if lastTrade['Count'] != 0:
            # if position is sold we do not care
            if float(lastTrade['Items'][-1]['btcBalance']) > 1.0:
                # START trade function
                origQty = (float(usdt_balance['free']) - 5000.0) / float(btc_price['price'])
                actualQty = 0
                while actualQty < origQty - 0.00001:
                    market_buy = client.order_market_buy(symbol='BTCUSDT', quantity=float(round(origQty - actualQty, 6)))
                    if market_buy['status'] == 'EXPIRED':
                        break
                    actualQty += float(market_buy['executedQty'])
                    time.sleep(0.5)

                mywallet = client.get_account()
                tradeTime = time.time()
                TradesDB = 'trades'
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(TradesDB)
                table.put_item(Item={
                    'side': 'REBUY',
                    'tradeTime': str(tradeTime),  # 'tradeTime': str(market_buy['transactTime']),
                    'price': str(float(market_buy['cummulativeQuoteQty'])/ float(market_buy['executedQty'])),
                    'origQty': str(market_buy['origQty']),
                    'executedQty': str(actualQty),
                    'status': str(market_buy['status']),
                    'btcBalance': str(mywallet['balances'][1]['free']),  # btc, do this when trades are complete
                    'USDTBalance': str(mywallet['balances'][-2]['free'])  # usdt
                })
                tradeMade = True
                # END trade function
        # END get positions before reset

    # If no trades, store balance
    if tradeMade == False:
        TradesDB = 'trades'
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TradesDB)

        mywallet = client.get_account()
        tradeTime = time.time()
        table.put_item(Item={
            'side': 'None',
            'tradeTime': str(tradeTime),  # 'tradeTime': str(market_buy['transactTime']),
            # 'price': str(-1),
            # 'origQty': str(-1),
            # 'executedQty': str(-1),
            # 'status': str(-1),
            'btcBalance': str(mywallet['balances'][1]['free']),  # btc, do this when trades are complete
            'USDTBalance': str(mywallet['balances'][-2]['free'])  # usdt
        })
    # END place orders

    # delete old entries where no trade was made
    DB_NAME = 'trades'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DB_NAME)
    recentFilter = 660  # 11 minutes in UNix time
    trades = table.query(
        KeyConditionExpression=Key('side').eq("None")
                               & Key('tradeTime').lt(str(time.time() - recentFilter)),
    )

    for item in trades['Items']:
        table.delete_item(
            Key={
                'side': "None",
                'tradeTime': item['tradeTime']
            }
        )
    return('1')