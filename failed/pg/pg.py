from webbrowser import get
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



def get_local_time(ts):
    UTC_OFFSET = 14400000
    # ts = int(time.time())
    lt = datetime.utcfromtimestamp((ts+UTC_OFFSET)/1000).strftime('%d-%m-%Y %H:%M:%S')
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

def get_signal():
    st = int(time.time())
    # btc_24hr_pc = get_btc_24hr_price_change_percent()
    btc_24hr_pc = 0.0
    print('btc_24hr_pc', btc_24hr_pc)
    end_ts = int(time.time())*1000
    start_ts = end_ts - 2591999000
    # start_ts = end_ts - OFFSET_24HR
    for idx, pair in enumerate(pairs_list):
        tm = datetime.utcfromtimestamp(int(time.time())+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
        print(f'\r{idx}: {tm} working on {pair}            ', end="")
        d = get_historical_data(client, pair, start_ts, end_ts)

        df = pd.DataFrame(d)
        df.columns = ['unix_ts', 'open', 'high', 'low', 'close', 'Volume', 'close time', 'Quote asset' 'volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']

        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        wt_df=TA.WTO(df,14,21)
        df['wt1'] = wt_df['WT1.']
        df['wt2'] = wt_df['WT2.']

        df['previous_wt1'] = df['wt1'].shift(1)
        df['previous_wt2'] = df['wt2'].shift(1)
        df['crossing_down'] = (df['wt1'] <= df['wt2']) & (df['previous_wt1'] >= df['previous_wt2']) & (df['wt2'] >= WT_OVERBOUGHT )
        df['crossing_up'] = (df['wt1'] >= df['wt2']) & (df['previous_wt1'] <= df['previous_wt2']) & (df['wt2'] <= WT_OVERSOLD )
        df['signal']=np.where(df['crossing_up'] , 'long', (np.where(df['crossing_down'], 'short', 'no_sig')))
        sig = list(df['signal'])[-1]
        # lt = get_local_time()
        # df['local time'] = lt

        ndf = pd.DataFrame()

        unix_ts = list(df['unix_ts'])
        local_time = [get_local_time(i) for i in unix_ts]
        ndf['local_time'] = local_time
        ndf['signal'] = list(df['signal'])
        # ndf.to_csv(f'1M-BTC-5m.csv', sep=',', index=False)
        ndf.to_csv(f'1m-BTC-5m.csv', sep=',', index=False)

        # if (sig == 'long'):
        #     return {"asset": pair[:-4], "pos": "el"}
        # if (sig == "short"):
        #     return {"asset": pair[:-4], "pos": "es"}
    et = int(time.time())
    td = et-st
    print(f'finished in {td}s')
    return None

def send_alert(asset, pos):
    url = 'http://localhost/webhook'
    alert = {"type": pos, "strat_id": "V2_VMC_HK_5min", "asset": asset}
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

get_signal()
