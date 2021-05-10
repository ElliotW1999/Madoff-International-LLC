import pandas as pd
import matplotlib.pyplot as plt

btcPrices = pd.read_csv('gemini_BTCUSD_1hr.csv', header=1)
btcTrends = pd.read_csv('btcTrends.csv', header=0)

btcTrends = btcTrends[0:-10]
btcPrices = btcPrices[0:158]
btcPrices = btcPrices.iloc[::-1] # reverse the prices order

#print(btcPrices)
#print(btcTrends)

btcTrends = btcTrends["Bitcoin"]
btcPrices = btcPrices["Close"]

print(btcPrices.pct_change().to_string())
# the timestamp on trends corresponds to the hour -> hour:59

# we want to see if trend at T can predict btc close price at T (or T+1?)
plt.plot(1000*btcPrices.pct_change(), label="change in price")
plt.plot(btcTrends, label="interest")
plt.legend(loc="upper left")
plt.grid(axis='y')
plt.show()
