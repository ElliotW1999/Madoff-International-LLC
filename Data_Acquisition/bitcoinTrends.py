from pytrends.request import TrendReq
import pandas as pd

pytrends = TrendReq(hl='en-US', tz=0) #tz = 660?
kw_list = ["Bitcoin"]
pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
test = pytrends.interest_over_time()
print(test.to_string())
# = pytrends.build_payload("Bitcoin", cat=0, timeframe='now 7-d', geo='', gprop='')
test.to_csv('btcTrends.csv', index=True)

