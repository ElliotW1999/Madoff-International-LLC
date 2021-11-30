import os
import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

#sqlite_insert_with_param = """delete from tradesFeatures where date ='11-13-2021'"""
cur.execute(sqlite_insert_with_param)
conn.commit()
data = cur.fetchall()
print(data)

# 11-13-2021 has duplicates
#for date in dates:
#    data = """Select * from trades where date = """ + date
#    cur.execute(data)
#    data = cur.fetchall()
#    data = pd.DataFrame(data, columns=['date', 'time', 'price', 'size', 'isBuyerMaker'])
#    print(len(data))