import datetime
import pandas_datareader as web

if __name__ == "__main__":
    spy = web.DataReader(
        "SPY", "yahoo",
        datetime.datetime(2007,1,1),
        datetime.datetime(2021,1,1)
    )

print(spy.tail())
print(spy.size)