from binance.client import Client
from binance.enums import *
import pandas as pd
import time
import keys

apiKey = keys.apiKey
secretKey = keys.secretKey
client = Client(apiKey,secretKey)

posframe = pd.read_csv('strategy.csv')

def changePosition(curr,buy=True):
    if buy:
        posframe.loc[posframe.currency == curr, 'position'] = 1
    else:
        posframe.loc[posframe.currency == curr, 'position'] = 0
        
    posframe.to_csv('position',index=False)

def getDataHourly(symbol): #-> currency symbol
    frame = pd.DataFrame(client.get_historical_klines(symbol,'1h',
                                                     '25 hours ago UTC'))
    frame = frame.iloc[:,:5]
    frame.columns = ['Time','Open','High','Low','Close']
    frame[['Open','High','Low','Close']] = frame[['Open','High','Low','Close']].astype(float)
    frame.Time = pd.to_datetime(frame.Time,unit='ms')
    return frame

def applyTechnicals(df):
    df['FastSMA'] = df.Close.rolling(7).mean()
    df['SlowSMA'] = df.Close.rolling(24).mean()

def trader(curr):

    amount = posframe[posframe.currency == curr].quantity.values[0]
    df = getDataHourly(curr)
    applyTechnicals(df)
    lastrow = df.iloc[-1]
    if not posframe[posframe.currency == curr].position.values[0]:
        if lastrow.FastSMA > lastrow.SlowSMA:
            order = client.create_order(symbol=curr,side='BUY',type='MARKET',quantity=amount)
            print(order)
            print('satın aldm')
            changePosition(curr,buy=True)
        else:
            print(f'Not in position {curr} but Condition not fulfilled')
    
    else:
        print(f'Already in {curr} position')
        if lastrow.SlowSMA > lastrow.FastSMA:
            order = client.create_order(symbol=curr,side='SELL',type='MARKET',quantity=amount)
            print(order)
            print('sattım')
            changePosition(curr,buy=False)
        

def loop():
    try: 
        while True:
            for coin in posframe.currency:
                trader(coin)
            time.sleep(60)
    except KeyboardInterrupt:
        pass

loop()
