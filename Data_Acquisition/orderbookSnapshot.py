import os
import sqlite3
from sqlite3 import Error
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
month = "08"
day = "14"
date = month + "-" + day + "-2023"
newDate = "2023-" + month + "-" + day
table = dynamodb.Table('orderbookBinance_' + date)

# TODO: switch to table.query to get in batch
response = table.scan(
    FilterExpression=Key('date').eq(date)
)

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
            sqlite_insert_with_param = """INSERT INTO bids2023 (date, time, price, size) VALUES (?, ?, ?, ?);"""
            data_tuple = (newDate, snapshot['time'], bid[0], bid[1])
            cur.execute(sqlite_insert_with_param, data_tuple)

        for ask in snapshot['asks']:
            sqlite_insert_with_param = """INSERT INTO asks2023 (date, time, price, size) VALUES (?, ?, ?, ?);"""
            data_tuple = (newDate, snapshot['time'], ask[0], ask[1])
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

