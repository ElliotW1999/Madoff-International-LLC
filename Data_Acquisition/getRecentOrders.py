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
table = dynamodb.Table('recenttradesBinance_' + date)

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
        for i in range(0,len(snapshot['prices'])):
            sqlite_insert_with_param = """INSERT INTO trades2023 (date, time, isBuyerMaker, price, size) VALUES (?, ?, ?, ?, ?);"""
            data_tuple = (newDate, snapshot['time'], snapshot['isBuyerMaker'][i], snapshot['prices'][i],
                          snapshot['sizes'][i])
            cur.execute(sqlite_insert_with_param, data_tuple)

conn.commit()
print(date)

