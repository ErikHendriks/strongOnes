#!/usr/bin/env python3

import datetime
import json
import logging
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.trades as trades
import requests
import time
import urllib3

from decimal import Decimal
from oandapyV20 import API
from oandapyV20.contrib.requests import *
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.exceptions import V20Error, StreamTerminated
from requests.exceptions import ConnectionError
from sendInfo import sendEmail
from smas import sma

logging.basicConfig(
        filename='/var/log/strongOnes.log',
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',)

textList = []
textList.append('Oanda v20 strongones rapport at '+str(datetime.datetime.now()))
textList.append(' ')

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]
accountID = conf[0]
api = API(access_token = conf[1],\
                environment = conf[2])

symbols = ['AUD_CAD','AUD_CHF','AUD_JPY','AUD_NZD','AUD_USD',\
           'CAD_CHF','CAD_JPY',\
           'CHF_JPY',\
           'EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_JPY','EUR_NZD','EUR_USD',\
           'GBP_AUD','GBP_CAD','GBP_CHF','GBP_JPY','GBP_NZD','GBP_USD',\
           'NZD_CAD','NZD_CHF','NZD_JPY','NZD_USD','NZD_USD',\
           'USD_CAD','USD_CHF','USD_JPY']

ohlcd = {'count': 2,'granularity': 'D'}
params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
smaData30d1 = {'count': 30,'granularity': 'D'}
smaData50d1 = {'count': 50,'granularity': 'D'}
smaData100d1 = {'count': 100,'granularity': 'D'}
sma30d1 = {}
sma50d1 = {}
sma100d1 = {}
percentChangeDict = {}

r = positions.OpenPositions(accountID=accountID)
api.request(r)

for symbol in symbols:
    candle = InstrumentsCandles(instrument=symbol,params=ohlcd)
    api.request(candle)

    openPrice = float(candle.response['candles'][0]['mid']['o'])
    closePrice = float(candle.response['candles'][0]['mid']['c'])

    if 'JPY' in candle.response['instrument']:
        percentChangeDict[symbol] = round((closePrice - openPrice) / closePrice,3)
    else:
        percentChangeDict[symbol] = round((closePrice - openPrice) / closePrice,5)

    sma(symbol,sma30d1,smaData30d1)
    sma(symbol,sma50d1,smaData50d1)
    sma(symbol,sma100d1,smaData100d1)

r = trades.TradesList(accountID=accountID,params=params)
api.request(r)

for trade in r.response['trades']:
    if trade['initialUnits'] == '1000':
#       symbol = trade['instrument']
#       if sma30d1[symbol] < sma50d1[symbol] and\
#          sma50d1[symbol] < sma100d1[symbol]:
        r = trades.TradeClose(accountID=accountID, tradeID=trade['id'])
        rv = api.request(r)

    elif trade['initialUnits'] == '-1000':
#       symbol = trade['instrument']
#       if sma30d1[symbol] > sma50d1[symbol] and\
#          sma50d1[symbol] > sma100d1[symbol]:
        r = trades.TradeClose(accountID=accountID, tradeID=trade['id'])
        rv = api.request(r)

i = 0
j = 0
sortedReversed = sorted(percentChangeDict.items(), key=lambda x: x[1], reverse=True)
textList.append('Buy Orders:')
textList.append(' ')
while not (i==4 or j==6):
    for symbol,price in sortedReversed:
        print('i',i)
        print('j',j)
        if i==4 or j==6:
            break
        if sma30d1[symbol] > sma50d1[symbol] and\
           sma50d1[symbol] > sma100d1[symbol]:
            buyOrder = MarketOrderRequest(instrument=symbol,\
                        units=1000,)
            r = orders.OrderCreate(accountID, data=buyOrder.data)
            rv = api.request(r)
            textList.append(buyOrder)
            textList.append(' ')
            i+=1
            j+=1
        else:
            j+=1

i = 0
j = 0
sortedNoReversed = sorted(percentChangeDict.items(), key=lambda x: x[1])
textList.append('Sell Orders:')
textList.append(' ')
while not (i==4 or j==6):
    for symbol,price in sortedNoReversed:
        print('i',i)
        print('j',j)
        if i==4 or j==6:
            break
        if sma30d1[symbol] < sma50d1[symbol] and\
           sma50d1[symbol] < sma100d1[symbol]:
            sellOrder = MarketOrderRequest(instrument=symbol,\
                        units=-1000,)
            r = orders.OrderCreate(accountID, data=sellOrder.data)
            rv = api.request(r)
            textList.append(sellOrder)
            textList.append(' ')
            i+=1
            j+=1
        else:
            j+=1

text = '\n'.join(map(str,textList))
subject = 'StrongOnes.py rapport at '+str(datetime.datetime.now())
sendEmail(text,subject)
