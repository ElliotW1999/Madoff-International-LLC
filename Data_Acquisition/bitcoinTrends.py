from pytrends.request import TrendReq

print('helloworld')
pytrends = TrendReq(hl='en-US', tz=660) #tz = 660?
kw_list = ["Bitcoin"]
pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
test = pytrends.interest_over_time()
print(test)
# = pytrends.build_payload("Bitcoin", cat=0, timeframe='now 7-d', geo='', gprop='')
