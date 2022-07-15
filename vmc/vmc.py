# from signal import *
import numpy as np
import pandas as pd 

import time
import ccxt
from binance.client import Client
import datetime
import os.path 
from finta import TA
import datetime as dt
import pickle
import requests


url = 'http://34.122.102.91/webhook'

pairs_list = ['SOLUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'TRXUSDT', 'LTCUSDT', 'APEUSDT', 'AVAXUSDT', 'LINKUSDT', 'LITUSDT', 'GMTUSDT', 'DOTUSDT', 'FTMUSDT', 'GALAUSDT', 'SHIBUSDT', 'NEARUSDT', 'MATICUSDT', 'PEOPLEUSDT', 'SANDUSDT', 'MANAUSDT', 'VETUSDT', 'ATOMUSDT', 'LUNAUSDT', 'WAVESUSDT', 'JASMYUSDT', 'ENSUSDT', 'BCHUSDT', 'EGLDUSDT', 'RUNEUSDT', 'ETCUSDT', 'ZILUSDT', 'UNFIUSDT', 'FILUSDT', 'ALICEUSDT', 'AAVEUSDT', 'OPUSDT', 'ALGOUSDT', 'OGNUSDT', 'EOSUSDT', 'XLMUSDT', 'ICPUSDT', 'THETAUSDT', 'AXSUSDT', 'XMRUSDT', 'HNTUSDT', 'WOOUSDT', 'UNIUSDT', 'CHZUSDT', 'ROSEUSDT', 'SRMUSDT', 'TFUELUSDT', 'GALUSDT', 'STORJUSDT', 'FTTUSDT', 'ZECUSDT', 'ANCUSDT', 'LRCUSDT', 'API3USDT', 'BATUSDT', 'TWTUSDT', 'CAKEUSDT', 'BELUSDT', 'DYDXUSDT', 'GRTUSDT', 'RSRUSDT', 'FLMUSDT', 'CRVUSDT', 'ONEUSDT', 'BLZUSDT', 'QNTUSDT', 'POLSUSDT', 'XTZUSDT', 'JSTUSDT', 'GLMRUSDT', 'SUSHIUSDT', 'IMXUSDT', 'MASKUSDT', 'ARUSDT', 'NEOUSDT', 'SLPUSDT', 'CHRUSDT', 'ANTUSDT', 'DARUSDT', 'BNXUSDT', 'BTTCUSDT', 'WINUSDT', 'ONTUSDT', 'CELOUSDT', 'KNCUSDT', 'HBARUSDT', 'ENJUSDT', 'HOTUSDT', 'BAKEUSDT', 'IOTXUSDT', 'KDAUSDT', 'PONDUSDT', 'CITYUSDT', 'DUSKUSDT', 'IOTAUSDT', 'IOSTUSDT', 'DASHUSDT', 'MINAUSDT', 'SFPUSDT', 'MBLUSDT', 'SUNUSDT', 'TOMOUSDT', 'RVNUSDT', 'COMPUSDT', 'KLAYUSDT', 'GTCUSDT', 'MKRUSDT', 'SXPUSDT', 'QTUMUSDT', 'FETUSDT', 'KAVAUSDT', 'DENTUSDT', 'TCTUSDT', 'OMGUSDT', 'ATAUSDT', 'YFIUSDT', 'CELRUSDT', 'ANKRUSDT', 'FLOWUSDT', 'ZRXUSDT', 'LINAUSDT', 'LOKAUSDT', 'CTKUSDT', 'TLMUSDT', 'KP3RUSDT', 'COTIUSDT', 'C98USDT', 'KSMUSDT', 'AUDIOUSDT', 'ASTRUSDT', 'ZENUSDT', 'YFIIUSDT', 'WINGUSDT', 'POWRUSDT', 'CVXUSDT', 'QIUSDT', 'SPELLUSDT', 'UMAUSDT', 'OCEANUSDT', '1INCHUSDT', 'DODOUSDT', 'SNXUSDT', 'RENUSDT', 'NKNUSDT', 'REEFUSDT', 'BICOUSDT', 'BSWUSDT', 'BURGERUSDT', 'CTSIUSDT', 'BETAUSDT', 'PYRUSDT', 'MTLUSDT', 'ASRUSDT', 'PERPUSDT', 'TRBUSDT', 'STMXUSDT', 'ALPINEUSDT', 'MBOXUSDT', 'MOVRUSDT', 'BNTUSDT', 'XECUSDT', 'LDOUSDT', 'CTXCUSDT', 'RLCUSDT', 'BANDUSDT', 'IDEXUSDT', 'ARPAUSDT', 'YGGUSDT', 'POLYUSDT', 'ICXUSDT', 'EPXUSDT', 'SANTOSUSDT', 'AVAUSDT', 'RNDRUSDT', 'MIRUSDT', 'SKLUSDT', 'REPUSDT', 'ADXUSDT', 'OGUSDT', 'TROYUSDT', 'NEXOUSDT', 'TUSDT', 'NULSUSDT', 'SYSUSDT', 'AGLDUSDT', 'INJUSDT', 'VOXELUSDT', 'COCOSUSDT', 'WAXPUSDT', 'ACAUSDT', 'STXUSDT', 'LAZIOUSDT', 'DGBUSDT', 'XVSUSDT', 'SCRTUSDT', 'LPTUSDT', 'WRXUSDT', 'ILVUSDT', 'HIVEUSDT', 'RAYUSDT', 'PSGUSDT', 'CKBUSDT', 'CVCUSDT', 'BARUSDT', 'ELFUSDT', 'CFXUSDT', 'ALPHAUSDT', 'REQUSDT', 'COSUSDT', 'SCUSDT', 'FISUSDT', 'STPTUSDT', 'KEYUSDT', 'AUTOUSDT', 'PORTOUSDT', 'PLAUSDT', 'XNOUSDT', 'SUPERUSDT', 'QUICKUSDT', 'GTOUSDT', 'BIFIUSDT', 'ALCXUSDT', 'AKROUSDT', 'DIAUSDT', 'VGXUSDT', 'ORNUSDT', 'ATMUSDT', 'WNXMUSDT', 'XEMUSDT', 'FLUXUSDT', 'TORNUSDT', 'STRAXUSDT', 'FORUSDT', 'ACHUSDT', 'MITHUSDT', 'ALPACAUSDT', 'DREPUSDT', 'TRIBEUSDT', 'OOKIUSDT', 'XVGUSDT', 'ACMUSDT', 'MFTUSDT', 'STEEMUSDT', 'MULTIUSDT', 'RAMPUSDT', 'HIGHUSDT', 'UTKUSDT', 'BALUSDT', 'MDTUSDT', 'FARMUSDT', 'JUVUSDT', 'BTSUSDT', 'PUNDIXUSDT', 'DEGOUSDT', 'BTCSTUSDT', 'OXTUSDT', 'CLVUSDT', 'ERNUSDT', 'BTGUSDT', 'BEAMUSDT', 'TKOUSDT', 'MCUSDT', 'LTOUSDT', 'ONGUSDT', 'FORTHUSDT', 'RIFUSDT', 'RAREUSDT', 'DATAUSDT', 'MLNUSDT', 'TRUUSDT', 'FRONTUSDT', 'MDXUSDT', 'VIDTUSDT', 'REIUSDT', 'JOEUSDT', 'GNOUSDT', 'AMPUSDT', 'TVKUSDT', 'BADGERUSDT', 'CHESSUSDT', 'FIDAUSDT', 'VTHOUSDT', 'AUCTIONUSDT', 'WTCUSDT', 'AUCTIONUSDT', 'DOCKUSDT', 'DFUSDT', 'FIOUSDT', 'FIROUSDT', 'DNTUSDT', 'OMUSDT', 'MOBUSDT', 'LSKUSDT', 'WANUSDT', 'RADUSDT', 'PNTUSDT', 'NBSUSDT', 'BONDUSDT', 'AIONUSDT', 'PHAUSDT', 'GHSTUSDT', 'IRISUSDT', 'FUNUSDT', 'CVPUSDT', 'DEXEUSDT', 'KMDUSDT', 'PERLUSDT', 'NMRUSDT', 'VITEUSDT', 'DCRUSDT', 'ARDRUSDT']
# , 'GBPUSDT', 'FXSUSDT', 'EURUSDT', 'AUDUSDT'
print(f'Tracked Coins: {len(pairs_list)}')


trail=0.005
df_trades=pd.DataFrame()
new_candle_status= 'No'
balance_usdt =  1000  # 1000 $ virtual starting balance  ===== Comment when REAL TRADING ========
profit=0.01
bot_status='buy' 

wt_overbought=35
wt_oversold=-35



def read_pickle_file(fn):
    # with open(path_to_protocol5, "rb") as fh:
    with open(fn, 'rb') as handle:
        val = pickle.load(handle)
    print('read_pickle_file')
    return val

def get_client():
    fn = '/home/henokali1/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])



client = get_client() 



def get_historical_ohlc_data(symbol,past_days=None,interval=None):
    
    #Returns historcal klines from past for given symbol and interval
    #past_days: how many days back one wants to download the data
    
    if not interval:
        interval='1h' # default interval 1 hour
    if not past_days:
        past_days=30  # default past days 30.

    start_str=str((pd.to_datetime('today')-pd.Timedelta(str(past_days)+' days')).date())
    
    D=pd.DataFrame(client.get_historical_klines(symbol=symbol,start_str=start_str,interval=interval))
    D.columns=['open_time','open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol','is_best_match']
    D['open_date_time']=[dt.datetime.fromtimestamp(x/1000) for x in D.open_time]
    D['symbol']=symbol
    D=D[['symbol','open_date_time','open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol']]

    return D



"""
exchange = ccxt.kucoin({
    'apiKey': '********',
    'secret': '*********',
    'password':'*********',
    'enableRateLimit': True,})
  """  
    
exchange = ccxt.binance({
    'apiKey': '***********',
    'secret': '************',
    'enableRateLimit': True,}) 

file_status = os.path.exists('log.csv')
if file_status is False:

    columns=['Time','signal type','Asset','Amount in coin ','Blance in USDT','Price','target price','stop loss','Profit']
    data_log = pd.DataFrame(columns=columns)
    data_log.columns = columns
    data_log.to_csv('log.csv', mode='a', index=False, header=True)


def get_price(coinpair):
    all_coins = client.get_all_tickers()
    for i in all_coins:
        if (i['symbol'] == coinpair).all():
            return float(i['price'])
            

# ct stores current time
ct = datetime.datetime.now()
#print("current time:-", ct)
minutes = ct.strftime('%M')

time_left_minute =  60 - int(minutes)  # time left till the new candle data / start of the bot 
time_left_second =  time_left_minute * 60
print('Time till next new candle = ',time_left_second)
#time.sleep(time_left_second)
print('stat now')
"""
================================================================================================================
# set time for time_left then start the loop , each new candle will be at ( n ) interval, or in this case 60 min 

you have ti set shedule run for every 60 min, after time_left==0 

check currrent time then make sure the data is newer than it. this solve isseue of strting the bot anyime, and inside 
when you finish sellling a position and bot is free, update the variable of the time sstamp to new current 

so when finding time difference , make delay for that then run first candle check
if buy signal: wait to sell, get new time stamp then calculate the diff and add delay for
if no buy, just delay for


for backtesting code: 

check current price by gettting historical per minute, once there is clear sell signal/stop loss, sell and then 
drop all the values that match or older than the timestamp of the sell signal from the df data ( 1 hr df )
then repeat and record it in csv 

=================================================================================================================
"""
#wtOversold = wt2 <= wt_oversold
#wtOverbought = wt2 >= wt_overbought

def generate_signals(pairs_list):

    coins=list()
    for pair in pairs_list:

        globals()[f"ohlc_{pair}"] =get_historical_ohlc_data(symbol=pair,interval='1h')
        globals()[f"ohlc_{pair}"]['open']=pd.to_numeric(globals()[f"ohlc_{pair}"]['open'], errors='coerce')
        globals()[f"ohlc_{pair}"]['high']=pd.to_numeric(globals()[f"ohlc_{pair}"]['high'], errors='coerce')
        globals()[f"ohlc_{pair}"]['low']=pd.to_numeric(globals()[f"ohlc_{pair}"]['low'], errors='coerce')
        globals()[f"ohlc_{pair}"]['close']=pd.to_numeric(globals()[f"ohlc_{pair}"]['close'], errors='coerce')
        wt_df=TA.WTO( globals()[f"ohlc_{pair}"],14,21)
        globals()[f"ohlc_{pair}"]['wt1']=wt_df['WT1.']  #white wave 
        globals()[f"ohlc_{pair}"]['wt2']=wt_df['WT2.']  # blue wave 
        globals()[f"ohlc_{pair}"]['ATR']=TA.ATR(globals()[f"ohlc_{pair}"])
        previous_wt1 = globals()[f"ohlc_{pair}"]['wt1'].shift(1)
        previous_wt2 = globals()[f"ohlc_{pair}"]['wt2'].shift(1)
        crossing_down = (globals()[f"ohlc_{pair}"]['wt1'] <= globals()[f"ohlc_{pair}"]['wt2']) & (previous_wt1 >= previous_wt2) & (globals()[f"ohlc_{pair}"]['wt2'] >= wt_overbought )
        crossing_up = (globals()[f"ohlc_{pair}"]['wt1'] >= globals()[f"ohlc_{pair}"]['wt2']) & (previous_wt1 <= previous_wt2) & (globals()[f"ohlc_{pair}"]['wt2'] <= wt_oversold )
        globals()[f"ohlc_{pair}"]['signal']=np.where(crossing_up , 'buy', 
             (np.where(crossing_down, 'sell', 'watch')))

        globals()[f"ohlc_{pair}"].dropna(inplace=True)
        globals()[f"ohlc_{pair}"].reset_index(drop=True, inplace=True)
        coins.append(globals()[f"ohlc_{pair}"])

print ('ok here ')
while(True):
    print('inside while loop')
    ct = datetime.datetime.now()
    #print("current time:-", ct)
    minutes = ct.strftime('%M')
    time_left_minute =  60 - int(minutes)  # time left till the new candle data / start of the bot 
    time_left_second =  time_left_minute * 60
    print('time_left_minute = ' , time_left_minute)

    if  time_left_minute >= 59 :
        generate_signals(pairs_list)  # make it every n time, example 1 hr, 30 min 

        for pair in pairs_list:
            df=globals()[f"ohlc_{pair}"] 
            #print(df.iloc[-2]['signal'])
            #if df['signal'][i]== 'buy':
            if (df.iloc[-2]['signal']== 'buy' ) & (time_left_minute >= 59)  :
            # place while true loop to stay in this  
                # buy 
                df_trades=df_trades.append(df.iloc[-2])
                print(df.iloc[-2])
                print('================================')
                
                ATR= df.iloc[-2]['ATR']
                purchase_price = df.iloc[-2]['close']
                profit_target = purchase_price + ( purchase_price * profit)
                target_price = purchase_price +  (purchase_price * trail)
                stop_loss= purchase_price -  2*ATR
                trail_trigger = purchase_price +( purchase_price * trail )
                ticker = df['symbol'].replace('USDT','/USDT')
                # ============== Real Trading ==================
                """
                balance_usdt = ( balance['total']['USDT'] )   # make it just a variable/ number for paper trading , and save but sell csv
                amount = (balance_usdt/float(df['close'])) 
                order = exchange.create_order(ticker, 'limit' , 'buy', amount, float(df['close']))  
                asset_bought=(df['symbol']).replace('USDT','')
                time.sleep(3)
                balance = exchange.fetch_balance()
                bag= balance['free'][asset_bought]    # ammount holding of asset bought   #print both balance and bag
                """
                # ============== End Real Trading ==============

                # ========= paper trading  ================ 
                #balance_usdt =  1000  # 1000 $ virtual starting balance 
                #close_price = df['close'].astype(float)
                #amount =  (balance_usdt/close_price)
                ordered_qt = balance_usdt / purchase_price 
                asset_bought = (df.iloc[-2]['symbol']).replace('USDT','')
                bag = ordered_qt
                # ========= End Paper trading ==============
                time.sleep(10)

                # save to csv 

                data1 = {'Time':datetime.datetime.now(),'signal type': 'Buy' ,'Asset_bought': asset_bought,'Amount in coin ': bag ,'Blance in USDT':balance_usdt ,'price' : purchase_price, 'target price' : trail_trigger, 'stop loss' : stop_loss , 'Profit':'NAN' }
                data_log = pd.DataFrame(data1,index=[0]) 
                data_log.to_csv('log.csv', mode='a', index=False, header=False)
                #print(bot_status)
                bot_status = 'sell'
                #print(bot_status)
                
                # json={"type": "el", "strat_id": "VMC_MHD", "asset": asset_bought, "price" : purchase_price, "pnl": 0.0}
                # r = requests.post(url, json=json)

                while(bot_status == 'sell'):

                    time_now = datetime.datetime.now()
                    coinpair = df['symbol']
                    current_price = get_price(coinpair)
                    print('========================')
                    print('Time : ',time_now.hour,':',time_now.minute)
                    print('Asset Bought', asset_bought)
                    print('Purchase price', purchase_price)
                    print('Stop loss', stop_loss)
                    print('Target price', profit_target)
                    print('Trail trigger', trail_trigger)
                    print('current price', current_price)
                    time.sleep(10)
                    if current_price >= trail_trigger:
                        trail_trigger = current_price +( current_price * trail )
                        stop_loss= stop_loss + stop_loss*trail
                         
                    if (current_price <= stop_loss ) or ( current_price > profit_target ):
                        """
                        # ========= Real trading  ================ 
                        order = exchange.create_order(ticker, 'limit','sell', bag, current_price)
                        pofit_perc = 
                        # ============== End Real Trading ==============  """                  

                        # ========= paper trading  ================
                        balance_usdt_new = ( bag * current_price ) # add commision later
                        pofit_perc = (( balance_usdt_new - balance_usdt) / balance_usdt_new)*100
                        balance_usdt = balance_usdt_new
                        # ========= End Paper trading ==============

                        data1 = {'Time':datetime.datetime.now(),'signal type': 'Sell' ,'Asset_sold': asset_bought, 'Amount in coin ': bag ,'Blance in USDT':balance_usdt_new, 'Price' : current_price, 'target price' : trail_trigger, 'stop loss' : stop_loss,'Profit':pofit_perc }
                        data_log = pd.DataFrame(data1,index=[0])

                        data_log.to_csv('log.csv', mode='a', index=False, header=False)
                        bot_status == 'Buy'
                        ct = datetime.datetime.now()
                        minutes = ct.strftime('%M')
                        time_left_minute =  60 - int(minutes)  # time left till the new candle data / start of the bot 
                        time_left_second =  time_left_minute * 60
                        
                        # json={"type": "xl", "strat_id": "VMC_MHD", "asset": asset_bought, "price" : current_price, "pnl": pofit_perc}
                        # r = requests.post(url, json=json)
    
                        break;

    else:
        time_now = datetime.datetime.now()
        print('new_candle_status= No ')
        print('Time : ' , time_now)
        time.sleep(time_left_second)
