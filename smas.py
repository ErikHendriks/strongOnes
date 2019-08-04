import oandapyV20

from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
        environment = conf[2])

smaData30d1 = {'count': 30,'granularity': 'D'}
smaData50d1 = {'count': 50,'granularity': 'D'}
smaData100d1 = {'count': 100,'granularity': 'D'}
#sma30d1 = {}
#sma50d1 = {}
#sma100d1 = {}

#symbol='EUR_USD'

def sma(symbol,data,params):
    data[symbol] = 0.0
    candles = InstrumentsCandles(instrument=symbol,params=params)
    api.request(candles)
    for close in candles.response['candles']:
        data[symbol] += float(close['mid']['c'])
    print('len1 ',params['count'])
    data[symbol] = data[symbol] / params['count']
    print('len2 ',len(data))
    print(data)
    return data

def SMA30d1(symbol,sma30d1):
    sma30d1[symbol] = 0.0
    candles = InstrumentsCandles(instrument=symbol,params=smaData30d1)
    api.request(candles)
    for close in candles.response['candles']:
        sma30d1[symbol] += float(close['mid']['c'])
    sma30d1[symbol] = sma30d1[symbol] / 30
#   print('30d1  ',sma30d1[symbol])
    return sma30d1

def SMA50d1(symbol,sma50d1):
    sma50d1[symbol] = 0.0
    candles = InstrumentsCandles(instrument=symbol,params=smaData50d1)
    api.request(candles)
    for close in candles.response['candles']:
        sma50d1[symbol] += float(close['mid']['c'])
    sma50d1[symbol] = sma50d1[symbol] / 50
#   print('50d1  ',sma50d1[symbol])
    return sma50d1

def SMA100d1(symbol,sma100d1):
    sma100d1[symbol] = 0.0
    candles = InstrumentsCandles(instrument=symbol,params=smaData100d1)
    api.request(candles)
    for close in candles.response['candles']:
        sma100d1[symbol] += float(close['mid']['c'])
    sma100d1[symbol] = sma100d1[symbol] / 100
#   print('100d1 ',sma100d1[symbol])
    return sma100d1

symbol = 'EUR_USD'
data30 = {}
data50 = {}
data100 = {}
sma(symbol,data30,smaData30d1)
sma(symbol,data50,smaData50d1)
sma(symbol,data100,smaData100d1)
