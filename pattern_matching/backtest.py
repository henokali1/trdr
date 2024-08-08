from binance.client import Client
from binance.enums import *
from time import time
import pandas as pd
from pathlib import Path
import json
import pickle
from ast import literal_eval

downloads_path = str(Path.home() / "Downloads")
documents_path = str(Path.home() / "Documents")

backtest_raw_fn = f'{downloads_path}\\backtest_raw_hd.csv'

def get_client():
    fn = f'{documents_path}\\key\\binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])

def get_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

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
    df.to_csv(backtest_raw_fn, index=False)
    print('Historical Data Exported!\t', backtest_raw_fn)
    return df

def read_local_hd(fn):
    return pd.read_csv(fn)

def get_chunks(df):
    lst = list(df['close_pc'])
    r=[]
    tot = len(lst)
    for idx, val in enumerate(lst):
        if idx < chunk_size:
            r.append([0]*chunk_size)
        else:
            r.append(lst[idx-chunk_size:idx])
    df['raw_chunks'] = r
    # df.to_csv(f'{downloads_path}/raw_chunks.csv', index=False)
    # print('Raw Chunks Exported!', f'{downloads_path}/raw_chunks.csv')
    return df

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


def get_tst_chunks():
    hd = read_local_hd(backtest_raw_fn)
    close_pc_df = get_pc(hd)
    hd['close_pc'] = list(close_pc_df['pc'])
    chunks_df = get_chunks(hd)
    tst_chunks_df = pd.DataFrame()
    tst_chunks_df['ts'] = list(chunks_df['time'])
    tst_chunks_df['tst_chunks'] = list(chunks_df['raw_chunks'])
    tst_chunks_df.to_csv(f'{downloads_path}\\backtest_tst_chunks.csv', index=False)
    print(f'backtest tst Chunks Exported! {downloads_path}\\backtest_tst_chunks.csv')
    return tst_chunks_df

def save_dict_to_pickle(dictionary, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dictionary, file)
        print(f'Saved {filename}')

def load_dict_from_pickle(filename):
    with open(filename, 'rb') as file:
        dictionary = pickle.load(file)
    print(f'Reading {filename}')
    return dictionary

def format_ref(r_pkl):
    raw_ref_chunks_df = pd.read_csv(f'{downloads_path}/ref_chunks.csv')
    raw_ref_ts = list(raw_ref_chunks_df['ts'])
    raw_ref_chunk = list(raw_ref_chunks_df['ref_chunks'])
    raw_long_qualified = list(raw_ref_chunks_df['long_qualified'])
    raw_short_qualified = list(raw_ref_chunks_df['short_qualified'])

    formatted_ref = []
    for val in r_pkl:
        ref_ts = val['ref_ts']
        raw_ref_ts_idx = raw_ref_ts.index(ref_ts)

        r = {
            'avg_avg_dissimilarity': val['avg_avg_dissimilarity'],
            'pattern_occurrence': val['pattern_occurrence'],
            'ref_ts': ref_ts,
            'ref_chunks': literal_eval(raw_ref_chunk[raw_ref_ts_idx]),
            'long_qualified': raw_long_qualified[raw_ref_ts_idx],
            'short_qualified': raw_short_qualified[raw_ref_ts_idx]
        }
        formatted_ref.append(r)
    return formatted_ref

def format_elapsed_time(seconds):
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{days:03}d:{hours:02}h:{minutes:02}m:{seconds:02}s"

def all_zeros(lst):
    return all(x == 0 for x in lst)

def get_percent_dissimilarity(ref_lst_chunk, tst_lst_chunk):
    percent_dissimilarity = []
    for idx in range(len(ref_lst_chunk)):
        if ref_lst_chunk[idx] != 0:
            percent_dissimilarity.append(abs(round((tst_lst_chunk[idx]*100/ref_lst_chunk[idx])-100, 4)))
        else:
            percent_dissimilarity.append(9999)
    avg = round(sum(percent_dissimilarity)/len(percent_dissimilarity), 4)
    return avg

def measure_dissimilarity(ref_chunks_lst_dict, tst_chunks_lst_dict):
    r= []
    qualified_tst_ts_lst = []
    qualified_avg_dissimilarity_lst = []
    long_rois_lst = []
    short_rois_lst = []
    start_ts = time()
    tot = len(ref_chunks_lst_dict)
    backtest_raw_df = pd.read_csv(backtest_raw_fn)
    raw_ts = list(backtest_raw_df['time'])
    high_price = list(backtest_raw_df['high'])
    low_price = list(backtest_raw_df['low'])
    close_price = list(backtest_raw_df['close'])
    tst_tot = len(raw_ts)
    for ref_idx, ref_val in enumerate(ref_chunks_lst_dict):
        # if(ref_idx%10 == 0) and ref_idx != 0:
        if ref_idx != 0:
            completed = round(ref_idx*100/tot, 1)
            remaining = round(100-completed)
            cur_ts = time()
            ts_diff = int(cur_ts - start_ts)
            estimated_tm_to_complete = round(int(ts_diff*(tot-ref_idx)/ref_idx), 1)
            print(f"\rElapsed Time: {format_elapsed_time(ts_diff)} \t Completed: {completed}% \tRemaining: {remaining}% \tETA: {format_elapsed_time(estimated_tm_to_complete)}                               ", end="")
        for tst_idx, tst_val in enumerate(tst_chunks_lst_dict):
            if ((all_zeros(ref_val['ref_chunks'])) or (all_zeros(tst_val['tst_chunks'])) or (tst_val['tst_chunks'] == ref_val['ref_chunks'])):
                continue
            else:
                avg_dissimilarity = get_percent_dissimilarity(ref_val['ref_chunks'], tst_val['tst_chunks'])
                if (avg_dissimilarity <= dissimilarity_threshold) and ((tst_idx + chunk_size + 1) <= tst_tot): 
                    idx = raw_ts.index(tst_val['ts'])
                    cp = close_price[idx]
                    max_price = max(high_price[(idx+1):idx + chunk_size])
                    min_price = min(low_price[(idx+1):idx + chunk_size])
                    long_roi = round((max_price*100/cp)-100, 4)
                    short_roi = round((cp*100/min_price)-100, 4)
                    long_rois_lst.append(long_roi)
                    short_rois_lst.append(short_roi)
                    qualified_tst_ts_lst.append(tst_val['ts'])
                    qualified_avg_dissimilarity_lst.append(avg_dissimilarity)

        pattern_occurrence = len(qualified_avg_dissimilarity_lst)
        if (pattern_occurrence >= min_pattern_occurrence):
            avg_avg_dissimilarity = round(sum(qualified_avg_dissimilarity_lst)/pattern_occurrence, 4)
            ref_position_type = 'long' if ref_val['long_qualified'] else 'short'
            avg_pnl = 0
            if ref_position_type == 'long':
                avg_pnl = round(sum(long_rois_lst)/len(long_rois_lst), 2)
            else:
                avg_pnl = round(sum(short_rois_lst)/len(short_rois_lst), 2)

            r.append({
                'avg_avg_dissimilarity': avg_avg_dissimilarity,
                'pattern_occurrence': pattern_occurrence,
                'avg_pnl': avg_pnl,
                'ref_ts': ref_val['ref_ts'],
                'qualified_tst_ts_lst': qualified_tst_ts_lst,
                'qualified_avg_dissimilarity_lst': qualified_avg_dissimilarity_lst,
                'ref_position_type': ref_position_type,
                'long_rois_lst': long_rois_lst,
                'short_rois_lst': short_rois_lst,
            })
            save_dict_to_pickle(r, f'{downloads_path}\\backtest_r.pkl')
        qualified_tst_ts_lst = []
        qualified_avg_dissimilarity_lst = [] 
        long_rois_lst = []
        short_rois_lst = []
    print('\nExporting backtest_analyze.csv')
    dissimilarity_df = pd.DataFrame(r)
    dissimilarity_df.to_csv(f'{downloads_path}\\backtest_analyze.csv', index=False)
    print('backtest_analyze.csv Exported!')
    return dissimilarity_df

start_timestamp = 1672516800 #  January 1, 2023 12:00:00 AM GMT+04:00
end_timestamp = 1722988800 #  August 7, 2024 4:00:00 AM GMT+04:00


config = get_config('config.json')
candlestick = config['candlestick']
chunk_size = config['chunk_size']
roi_threshold = config['roi_threshold']
sm_threshold = config['sm_threshold']
min_pattern_occurrence = config['min_pattern_occurrence']
dissimilarity_threshold = config['dissimilarity_threshold']

# download_hd(start_timestamp, end_timestamp, candlestick)
hd = read_local_hd(backtest_raw_fn)
tst_chunks_df = get_tst_chunks()
tst_chunks_lst_dict = tst_chunks_df.to_dict(orient='records')

raw_ref = load_dict_from_pickle(f'{downloads_path}/r.pkl')
refs = format_ref(raw_ref)

dissimilarity = measure_dissimilarity(refs, tst_chunks_lst_dict)
