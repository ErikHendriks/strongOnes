#!/usr/bin/env python3

import datetime
import gnupg
import json
import logging
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import requests
import smtplib
import time
import urllib3

from decimal import Decimal
from oandapyV20 import API
from oandapyV20.contrib.requests import *
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.pricing import PricingStream
from oandapyV20.exceptions import V20Error, StreamTerminated
from requests.exceptions import ConnectionError

logging.basicConfig(
        filename='/var/log/strongOnes.log',
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',)

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

def sendEmail(text,subject):
        '''
        '''
        try:
                fingerprint = conf[3]
                password = conf[4]
                sender = conf[6]
                reciever = conf[5]
#               subject = 'Oanda v20 breakout test rapport at '+str(datetime.datetime.now())
                gpg = gnupg.GPG(gnupghome='/etc/breakout/.gnupg')
                text = str(gpg.encrypt(text,fingerprint))
                mail = '''From: %s\nTo: %s\nSubject: %s\n\n%s
                        ''' % (sender,reciever,subject,text)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender,password)
#               server.set_debuglevel(1)
                server.sendmail(sender, reciever, mail)
                server.quit()
        except Exception as e:
#               print(e)
                with open('/var/log/strongOnes.log', 'a') as LOG:
                        LOG.write(str(datetime.datetime.now()) + ' sendEmail: {}\n'.format(e))
                pass

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
ohlcm = {'count': 1,'granularity': 'M'}
ohlcd = {'count': 2,'granularity': 'D'}

params = {'instruments':'AUD_CAD,AUD_CHF,AUD_JPY,AUD_NZD,AUD_USD,CAD_CHF,CAD_JPY,CHF_JPY,EUR_AUD,EUR_CAD,EUR_CHF,EUR_GBP,EUR_JPY,EUR_NZD,EUR_USD,GBP_AUD,GBP_CAD,GBP_CHF,GBP_JPY,GBP_NZD,GBP_USD,NZD_CAD,NZD_CHF,NZD_JPY,NZD_USD,NZD_USD,USD_CAD,USD_CHF,USD_JPY'}
price = PricingStream(accountID=accountID,params=params)
date = datetime.datetime.now()

#for p in api.request(price):
#   print(p)
percentChangeDict = {}

r = positions.OpenPositions(accountID=accountID)
api.request(r)
#print(r.response)

for symbol in symbols:
    candle1 = InstrumentsCandles(instrument=symbol,params=ohlcm)
    candle2 = InstrumentsCandles(instrument=symbol,params=ohlcd)
    api.request(candle1)
    api.request(candle2)

#   closem1 = float(candle1.response['candles'][0]['mid']['c'])
#   closed1 = float(candle2.response['candles'][0]['mid']['c'])
#   closed2 = float(candle2.response['candles'][1]['mid']['c'])
    openPrice = float(candle2.response['candles'][0]['mid']['o'])
    closePrice = float(candle2.response['candles'][0]['mid']['c'])

#   diffToday = round(Decimal((closem1 - closed1) / closem1),5)
#   diffYesterday = round(Decimal((closed1 - closed2) / closed1),5)

#   print(candle2.response['instrument'])
#   print(closePrice)
#   print(openPrice)
    if 'JPY' in candle2.response['instrument']:
        percentChangeDict[symbol] = round((closePrice - openPrice) / closePrice,3)
    else:
        percentChangeDict[symbol] = round((closePrice - openPrice) / closePrice,5)

#print(sorted(percentChangeDict.items(), key=lambda x: x[1], reverse=True))



i = 0
textList.append('Buy Orders:')
textList.append(' ')
while i < 5:
    buyOrder = MarketOrderRequest(instrument=sorted(percentChangeDict.items(), key=lambda x: x[1], reverse=True)[i][0],\
                units=1000,)
    r = orders.OrderCreate(accountID, data=buyOrder.data)
    rv = api.request(r)
    textList.append(buyOrder)
    textList.append(' ')
    i+=1

i = 0
textList.append('Sell Orders:')
textList.append(' ')
while i < 5:
    sellOrder = MarketOrderRequest(instrument=sorted(percentChangeDict.items(), key=lambda x: x[1])[i][0],\
                units=-1000,)
    r = orders.OrderCreate(accountID, data=sellOrder.data)
    rv = api.request(r)
    textList.append(sellOrder)
    textList.append(' ')
    i+=1

text = '\n'.join(map(str,textList))
subject = 'StrongOnes.py rapport at '+str(datetime.datetime.now())
sendEmail(text,subject)
