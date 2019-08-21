import oandapyV20

from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
        environment = conf[2])

def sma(symbol,data,params):
    data[symbol] = 0.0
    candles = InstrumentsCandles(instrument=symbol,params=params)
    api.request(candles)
    for close in candles.response['candles']:
        data[symbol] += float(close['mid']['c'])
    data[symbol] = data[symbol] / params['count']
    return data

