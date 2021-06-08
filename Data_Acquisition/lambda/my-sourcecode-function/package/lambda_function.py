from datetime import datetime
import requests
import boto3

def lambda_handler(event, context):   
    btc_usd_ticker = requests.get('https://api-public.sandbox.pro.coinbase.com/products/BTC-USD/book?level=3').json()
    bestBid = btc_usd_ticker['bids'][0][0]
    dataframe = ['bids,']
    for order in btc_usd_ticker['bids']:
        # break out if price is +- 25%
        if (float(order[0]) < (3*float(bestBid)/4)):
            break
        else:
            dataframe += [order[0] + "," + order[1] + ""]

    dataframe += ['asks,']
    bestAsk = btc_usd_ticker['asks'][0][0]
    print(bestAsk)
    for order in btc_usd_ticker['asks']:
        if (float(order[0]) > (float(bestAsk)*1.25)):
            break
        else:
            dataframe += [order[0] + "," + order[1] + ""]
    
    AWS_BUCKET_NAME = 'orderbookdatastore'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    path = datetime.now().strftime("%m-%d-%Y,%H_%M_%S")
    data = bytes(dataframe)
    bucket.put_object(
        ACL='public-read',
        ContentType='application/json',
        Key=path,
        Body=data,
    )
    
    print(btc_usd_ticker)
    print('1')
    return '1'

