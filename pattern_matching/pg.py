
from binance.client import Client
from binance.enums import *
from time import time
import pickle as pickle
from datetime import datetime
import pandas as pd
from pathlib import Path
from datetime import datetime
import json


downloads_path = str(Path.home() / "Downloads")
documents_path = str(Path.home() / "Documents")
tst_fn = f'{downloads_path}\\hd.csv'
hd_dl_fn = f'{downloads_path}\\hd_dl.csv'
qualifying_trades_fn = f'{downloads_path}\\qualifying_trades.csv'


def get_client():
    fn = f'{documents_path}\\key\\binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])

def get_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def get_chunks(lst, chunk_size):
    r=[]
    tot = len(lst)
    for idx, val in enumerate(lst):
        end_idx = idx+chunk_size
        if end_idx <= tot:
            r.append(lst[idx:end_idx])
    return r

def get_pc(hd_df):
    close_price = list(hd_df['close'])
    ts = list(hd_df['time'])
    pc = []
    for idx, val in enumerate(close_price):
        if idx==0:
            pc.append({'time': ts[0], 'pc': 0})
        else:
            previous_price = close_price[idx-1]
            current_price = val
            pc_val = (round((current_price*100/previous_price)-100, 4))
            pc.append({'time': ts[idx], 'pc': pc_val})
    pc_df = pd.DataFrame(pc)
    return pc_df

def get_trades(hd_df, chunk_size):
    close_price = list(hd_df['close'])
    high_price = list(hd_df['high'])
    low_price = list(hd_df['low'])
    longs=[]
    shorts=[]
    long_qualified = []
    short_qualified = []
    tot = len(close_price)
    for idx in range(len(close_price)):
        if (idx + chunk_size) <= tot:
            cp = close_price[idx]
            max_price = max(high_price[idx:idx + chunk_size])
            min_price = min(low_price[idx:idx + chunk_size])
            long_roi = round((max_price*100/cp)-100, 4)
            short_roi = round((cp*100/min_price)-100, 4)
            longs.append({'long': long_roi})
            long_qualified.append(long_roi >= roi_threshold)
            shorts.append({'short': short_roi})
            short_qualified.append(short_roi >= roi_threshold)
        else:
            long_roi = 0.0
            short_roi = 0.0
            longs.append({'long': long_roi})
            long_qualified.append(False)
            shorts.append({'short': short_roi})
            short_qualified.append(False)
    long_trades_df = pd.DataFrame(longs)
    short_trades_df = pd.DataFrame(shorts)
    long_qualified_df = pd.DataFrame(long_qualified)
    short_qualified_df = pd.DataFrame(short_qualified)
    return long_trades_df, short_trades_df, long_qualified, short_qualified

def download_hd(start_timestamp, end_timestamp, candlestick): 
    client = get_client()
    data = []
    tot = (end_timestamp - start_timestamp)/(900*500)
    cntr = 0
    for current_sts in range(start_timestamp, end_timestamp+1, 900*500):
        next_ets = current_sts + 900*500 if (current_sts + 900*500) < end_timestamp else end_timestamp
        print(current_sts, next_ets, f'100% completed') if next_ets == end_timestamp else print(current_sts, next_ets, f'{round(cntr*100/tot, 1)}% completed')
        cntr += 1
        
        klines = client.futures_historical_klines('BTCUSDT', candlestick, current_sts*1000, next_ets*1000, limit=500)
        
        for kline in klines:
            timestamp = kline[0]/1000
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            data.append([timestamp, open_price, high_price, low_price, close_price, volume])

    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df.to_csv(hd_dl_fn, index=False)
    print('Historical Data Exported!\t', hd_dl_fn)
    return df

def read_local_hd(fn):
    return pd.read_csv(fn)

def get_qualifying_trades(df):
    close_pc_df = get_pc(df)
    long_trades_df, short_trades_df, long_qualified, short_qualified = get_trades(df, chunk_size)
    df['close_pc'] = close_pc_df['pc']
    df['long'] = long_trades_df
    df['short'] = short_trades_df
    df['long_qualified'] = long_qualified
    df['short_qualified'] = short_qualified
    df.to_csv(qualifying_trades_fn, index=False)
    print('Qualifying Trades Data Exported!', qualifying_trades_fn)
    return df

def get_chunks(qt_df):
    lst = list(qt_df['close_pc'])
    r=[]
    tot = len(lst)
    for idx, val in enumerate(lst):
        if idx < chunk_size:
            r.append([0]*chunk_size)
        else:
            r.append(lst[idx-chunk_size:idx])
    qt_df['ref_chunks'] = r
    qt_df.to_csv(f'{downloads_path}/ref_chunks.csv', index=False)
    print('Ref Chunks Exported!', f'{downloads_path}/ref_chunks.csv')
    return qt_df

def get_tst_chunks(ref_chunks_df):
    long_qualified = list(ref_chunks_df['long_qualified'])
    short_qualified = list(ref_chunks_df['short_qualified'])
    ref_chunks_lst = list(ref_chunks_df['ref_chunks'])
    r=[]
    tst_lst = []
    chunk_diff_lst = []
    for idx in range(len(long_qualified)):
        if (idx < chunk_size) or ((long_qualified[idx] == False) and (short_qualified[idx] == False)) :
            r.append(None)
            chunk_diff_lst.append(None)
        else:
            if (long_qualified[idx] == True) or (short_qualified[idx] == True):
                r.append(ref_chunks_lst[idx])
                tst_lst.append(ref_chunks_lst[idx])

    ref_chunks_df['tst_chunks'] = r
    ref_chunks_df['sm'] = chunk_diff_lst
    ref_chunks_df.to_csv(f'{downloads_path}/tst_chunks.csv', index=False)
    print('TST Chunks Exported!', f'{downloads_path}/tst_chunks.csv')
    return ref_chunks_df, tst_lst

config = get_config('config.json')
candlestick = config['candlestick']
chunk_size = config['chunk_size']
roi_threshold = config['roi_threshold']
sm_threshold = config['sm_threshold']

start_timestamp = 1609459200 #  January 1, 2021 12:00:00 AM
end_timestamp = 1719721304

# ref_chunks = get_chunks(pc_ref)
# tst_chunks = get_chunks(pc_tst)
# hd = read_local_hd(hd_dl_fn)
# qt_df = get_qualifying_trades(hd)

# ref_chunks_df = get_chunks(qt_df)
# tst_chunks_df, tst_lst = get_tst_chunks(ref_chunks_df)

tst_chunks_df = pd.read_csv(f'{downloads_path}/tst_chunks.csv')
close_price_lst = list(tst_chunks_df['close'])
high_price_lst = list(tst_chunks_df['high'])
ref_chunks_lst_str = list(tst_chunks_df['ref_chunks'])
tst_chunks_lst_str = list(tst_chunks_df['tst_chunks'])
long_qualified_lst = list(tst_chunks_df['long_qualified'])
ts = list(tst_chunks_df['time'])
ts = [int(i) for i in ts]
long = list(tst_chunks_df['long'])
short = list(tst_chunks_df['short'])



import math
import ast
from time import time

from typing import List, Dict

def sort_dicts_by_value(dicts: List[Dict], key: str) -> List[Dict]:
    """
    Sorts a list of dictionaries by the specified key value.

    :param dicts: List of dictionaries to be sorted
    :param key: The key by which the dictionaries should be sorted
    :return: A list of dictionaries sorted by the specified key
    """
    try:
        return sorted(dicts, key=lambda x: x[key])
    except KeyError:
        raise KeyError(f"One or more dictionaries do not have the key '{key}'")
    except TypeError:
        raise TypeError(f"The value for key '{key}' is not comparable")

def all_zeros(lst):
    return all(x == 0 for x in lst)

def format_elapsed_time(seconds):
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return f"{days:03}d:{hours:02}h:{minutes:02}m:{seconds:02}s"

# math.isnan(tst_chunks_lst[110])
def chunk_diff(ref_lst, tst_lst):
    cntr = 0
    chunk_size = len(tst_lst[0])
    sm_lst = []
    tot = len(tst_lst)
    start_ts = int(time())
    for tst_lst_idx,tst_val in enumerate(tst_lst):
        tst_lst_idx += 1
        if(tst_lst_idx%10 == 0) and tst_lst_idx != 0:
            completed = round(tst_lst_idx*100/tot, 1)
            remaining = round(100-completed)
            cur_ts = time()
            ts_diff = int(cur_ts - start_ts)
            estimated_tm_to_complete = round(int(ts_diff*(tot-tst_lst_idx)/tst_lst_idx), 1)
            print(f"Elapsed Time: {format_elapsed_time(ts_diff)} \t Completed: {completed}% \tRemaining: {remaining}% \tETA: {format_elapsed_time(estimated_tm_to_complete)}")
        for ref_idx,ref_val in enumerate(ref_lst):
            diff = []
            if(all_zeros(ref_val)) or (all_zeros(tst_val) or (tst_val == ref_val)):
                continue
            else:
                for k in range(chunk_size):
                    diff.append(abs(tst_val[k] - ref_val[k]))
                cntr += 1
                sm = round(sum(diff), 2)
                if sm <= sm_threshold:
                    pattern_id = f'{ts[ref_idx]}_{candlestick}_{chunk_size}_{roi_threshold}_{sm_threshold}'
                    long_roi = long[ref_idx]
                    short_roi = short[ref_idx]
                    sm_lst.append({'sm': sm, 'pattern_id': pattern_id, 'long_roi': long_roi, 'short_roi': short_roi, 'ref': ref_val, 'tst': tst_val})
    return sm_lst

def str_to_lst(val):
    try:
        return ast.literal_eval(val)
    except ValueError as e:
        return math.isnan(val)

# for idx in range(len(long_qualified_lst)):

tst_val_lst = []
for i in tst_chunks_lst_str:
    v = str_to_lst(i)
    if type(v) == type([1]):
        tst_val_lst.append(v)

tst_val_lst = tst_val_lst[:400]
ref_chunks_lst = [str_to_lst(i) for i in ref_chunks_lst_str]
chunk_diff_lst = chunk_diff(ref_chunks_lst, tst_val_lst)
print('Calculating sdbv...')
sdbv = sort_dicts_by_value(chunk_diff_lst, 'sm')

for i in range(100):
    print(sdbv[i])
