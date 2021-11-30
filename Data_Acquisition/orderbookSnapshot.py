import os
import sqlite3
from sqlite3 import Error
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
date = "11-28-2021"
table = dynamodb.Table('orderbookBinance_' + date)

# TODO: switch to table.query to get in batch
response = table.scan(
    FilterExpression=Key('date').eq(date)
)
print(response)
data = []
data.append(response)

while 'LastEvaluatedKey' in response:
    print('reading pages')
    response = table.scan(
        FilterExpression=Key('date').eq(date),
        ExclusiveStartKey=response['LastEvaluatedKey']
    )
    data.append(response)
    try:
        response['LastEvaluatedKey']  # exit loop when all data has been consumed
    except KeyError:
        break

#TODO: can use pandas to save in batch

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

for response in data:
    for snapshot in response['Items']:
        for bid in snapshot['bids']:
            sqlite_insert_with_param = """INSERT INTO bids (date, time, price, size) VALUES (?, ?, ?, ?);"""
            data_tuple = (snapshot['date'], snapshot['time'], bid[0], bid[1])
            cur.execute(sqlite_insert_with_param, data_tuple)

        for ask in snapshot['asks']:
            sqlite_insert_with_param = """INSERT INTO asks (date, time, price, size) VALUES (?, ?, ?, ?);"""
            data_tuple = (snapshot['date'], snapshot['time'], ask[0], ask[1])
            cur.execute(sqlite_insert_with_param, data_tuple)
conn.commit()
print(date)
# Visualise
#bids['bucket'] = [int(str(x)[:3]) for x in bids['price']]
#bids.set_index('bucket', drop=True)
#bids = bids.drop('price', axis=1)
#bidsGrouped = bids.groupby('bucket')
#fig, ax = plt.subplots(figsize=(16, 16))
#ax = sns.heatmap(bidsGrouped.sum(), cmap="Reds", annot=True)
#plt.yticks(rotation=0)
#plt.show()


# end Visualise

