import os
import numpy as np
import sqlite3
from sqlite3 import Error
#import pyqtgraph #switch to pyqtgraph eventually...
import matplotlib.pyplot as plt

db_file = os.path.dirname(os.path.dirname( __file__ ))+"/Data/tickers.db"

print(db_file)
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

cur.execute("SELECT * FROM price")
data = cur.fetchall()
closePrices = [x[4] for x in data]
volume = [x[5] for x in data]

# Have to investigate using ATR vs historical volatility, using the latter for now
logReturns = [round(np.log(j/i), 3) for i, j in zip(closePrices[:-1], closePrices[1:])] # np.log(j/i) - 1 ?
print(logReturns[47:55])
returnsAvg = np.mean(logReturns)
returnsDeviation = np.std(logReturns)

periodsRoot = 14 # 14^2 = 196 which ~= 195. This makes computation faster
volumeAvg = np.median(volume)                                 # we use the median because the data is strongly skewed
volumeDeviation = np.mean(np.absolute(volume - volumeAvg))    # std dev is not used as the data is skewed
print(volumeDeviation)
test = [[volume.index(i),i] for i in volume if i > volumeAvg + (5*volumeDeviation)]


priceOutliers = [[logReturns.index(i),i] for i in logReturns if i > returnsAvg + 2*returnsDeviation
         or i < returnsAvg - 2*returnsDeviation]
print(test)
print(priceOutliers)

fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(volume)
axs[0, 0].scatter([x[0] for x in test], [x[1] for x in test], c='#FF0000', marker='x')
axs[1, 0].plot(logReturns)
axs[1, 0].scatter([x[0] for x in priceOutliers], [x[1] for x in priceOutliers], c='#FF0000', marker='x')

axs[0, 1].hist(volume, 25)
axs[1, 1].hist(logReturns, 25)
axs[0, 0].set_title("Time-series")
axs[0, 0].set(ylabel="Volume")
axs[0, 1].set_title("Histogram")
axs[1, 0].set(ylabel="log Returns")
plt.show()