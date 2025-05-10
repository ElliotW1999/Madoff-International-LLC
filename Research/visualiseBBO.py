import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd

db_file = os.path.dirname(os.path.dirname(__file__)) + "/Data/binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

BBO = """Select * from BBO"""
cur.execute(BBO)
BBO = cur.fetchall()
BBO = pd.DataFrame(BBO, columns=['date', 'time', 'bestBid', 'bestAsk'])

fig, axs = plt.subplots(2)
axs[0].plot(BBO['bestAsk'])
axs[1].plot(BBO['bestAsk'] - BBO['bestBid'])

plt.show()


