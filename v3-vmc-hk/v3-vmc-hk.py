import pandas as pd 
import numpy as np
import time
from binance.client import Client
import datetime
from datetime import datetime
from finta import TA
import datetime as dt
import pickle
import requests



def get_local_time():
    UTC_OFFSET = 14400
    ts = int(time.time())
    lt = datetime.utcfromtimestamp(ts+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
    return lt

def read_pickle_file(fn):
    with open(fn, 'rb') as handle:
        val = pickle.load(handle)
    print('read_pickle_file')
    return val

def get_client():
    fn = '/home/henokali1/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])

def get_historical_data(client, coin_pair, start_ts, end_ts):
    return client.get_historical_klines(coin_pair, Client.KLINE_INTERVAL_5MINUTE, start_ts, end_ts)
    # return client.get_historical_klines(coin_pair, Client.KLINE_INTERVAL_1HOUR, start_ts, end_ts)

def get_btc_24hr_price_change_percent():
    try:
        ts = int(time.time())*1000
        cur_start = ts - OFFSET_1MIN
        cur_end = ts
        yest_start = ts - OFFSET_24HR - OFFSET_1MIN
        yest_end = ts - OFFSET_24HR
        openPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(yest_start), str(yest_end))[0][1])
        lastPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(cur_start), str(cur_end))[0][1])
        priceChangePercent = (lastPrice - openPrice )/(openPrice)*100
        return round(priceChangePercent, 2)
    except:
        return 0.0

def get_last_ts(fn):
    df = pd.read_csv(fn)
    val = list(df['unix_ts'])[-1]
    return int(val)

def update_df(nw_fn, old_fn):
    old_df = pd.read_csv(old_fn)
    nw_df = pd.read_csv(nw_fn)
    merged_df = pd.concat([old_df,nw_df]).drop_duplicates()
    merged_df.to_csv(old_fn, sep=',', index=False)
    print('df updated')

def get_signal():
    start_ts = 1660508100000
    # start_ts = get_last_ts('df-binance-raw-5min-BTC.csv')
    end_ts = int(time.time())*1000
    for idx, pair in enumerate(pairs_list):
        # tm = datetime.utcfromtimestamp(int(time.time())+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
        # print(f'\r{idx}: {tm} working on {pair}            ', end="")
        d = get_historical_data(client, pair, start_ts, end_ts)
        df = pd.DataFrame(d)
        df.columns = ['unix_ts', 'open', 'high', 'low', 'close', 'Volume', 'close time', 'Quote asset' 'volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
        # df.to_csv('df-binance-raw-5min-BTC.csv', sep=',')
        n_data = {'unix_ts': list(df['unix_ts']), 'open': list(df['open']), 'high': list(df['high']), 'low': list(df['low']), 'close': list(df['close']), 'Volume': list(df['Volume']), 'close time': list(df['close time'])}
        pd.DataFrame(n_data).to_csv('df-binance-raw-5min-BTC.csv', sep=',', index=False)
        # update_df('nw-df-5min-BTC.csv', 'df-binance-raw-5min-BTC.csv')


        # df.columns = ['unix_ts', 'open', 'high', 'low', 'close', 'Volume', 'close time', 'Quote asset' 'volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']


    #     df['open'] = pd.to_numeric(df['open'], errors='coerce')
    #     df['high'] = pd.to_numeric(df['high'], errors='coerce')
    #     df['low'] = pd.to_numeric(df['low'], errors='coerce')
    #     df['close'] = pd.to_numeric(df['close'], errors='coerce')
    #     wt_df=TA.WTO(df,14,21)
    #     df['wt1'] = wt_df['WT1.']
    #     df['wt2'] = wt_df['WT2.']

    #     df['previous_wt1'] = df['wt1'].shift(1)
    #     df['previous_wt2'] = df['wt2'].shift(1)
    #     df['crossing_down'] = (df['wt1'] <= df['wt2']) & (df['previous_wt1'] >= df['previous_wt2']) & (df['wt2'] >= WT_OVERBOUGHT )
    #     df['crossing_up'] = (df['wt1'] >= df['wt2']) & (df['previous_wt1'] <= df['previous_wt2']) & (df['wt2'] <= WT_OVERSOLD )
    #     df['signal']=np.where(df['crossing_up'] , 'long', (np.where(df['crossing_down'], 'short', 'no_sig')))
    #     sig = list(df['signal'])[-1]
    #     lt = get_local_time()
    #     # df.to_csv(f'df-logs/BTC-5m-{lt}.csv', sep=',', index=False)
    #     if (sig == 'long'):
    #         return {"asset": pair[:-4], "pos": "el"}
    #     if (sig == "short"):
    #         return {"asset": pair[:-4], "pos": "es"}
    # return None

def send_alert(asset, pos):
    url = 'http://localhost/webhook'
    alert = {"type": pos, "strat_id": "V3_VMC_HK_5min", "asset": asset}
    r = requests.post(url, json=alert)
    print('r', r)
    print('status', r.status_code)

def get_price(coin):
    coin = f'{coin}USDT'
    all_prices = client.get_all_tickers()
    for pair in all_prices:
        if pair['symbol'] == coin:
            return float(pair['price'])
    return None

# CONSTANTS
pairs_list = ['BTCUSDT']
blacklist = []
# Remove black listed coins
for pair in blacklist:
    if pair in pairs_list:
        pairs_list.remove(pair)


client = get_client()
UTC_OFFSET = 14400
OFFSET_24HR = 86400000
OFFSET_1MIN = 60000
WT_OVERBOUGHT=-104
WT_OVERSOLD=115
REQ_MIN = [0]
REQ_SEC = [1]
MODE = 'GET_SIG'

print('MODE:', MODE)

# while 1:
#     if MODE == 'GET_SIG':
#         ts = (time.time())
#         mnt = int(datetime.utcfromtimestamp(ts).strftime('%M'))
#         sec = int(datetime.utcfromtimestamp(ts).strftime('%S'))
#         if (mnt%5 == 0) and (sec in REQ_SEC):
#             print(f'Tracking {len(pairs_list)} Coins, {len(blacklist)} Blacklisted Coins')
#             sig = get_signal()
#             print(sig)
#             # sig = {"asset": "SOL", "pos": "es"}
#             if sig != None:
#                 asset = sig['asset']
#                 pos = sig['pos']
#                 if (pos == "el"):
#                     send_alert(asset, "xs")
#                     send_alert(asset, "el")
#                 if (pos == "es"):
#                     send_alert(asset, "xl")
#                     send_alert(asset, "es")
#         time.sleep(1)

get_signal()
