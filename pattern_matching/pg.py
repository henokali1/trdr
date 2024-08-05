import pandas as pd
from pathlib import Path
import json
from time import time



downloads_path = str(Path.home() / "Downloads")
documents_path = str(Path.home() / "Documents")
hd_dl_fn = f'{downloads_path}\\hd_dl.csv'
qualifying_trades_fn = f'{downloads_path}\\qualifying_trades.csv'




def get_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

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

def get_qualifying_trades(df):
    close_pc_df = get_pc(df)
    long_trades_df, short_trades_df, long_qualified, short_qualified = get_trades(df, chunk_size)
    df['close_pc'] = close_pc_df['pc']
    df['long'] = long_trades_df
    df['short'] = short_trades_df
    df['long_qualified'] = long_qualified
    df['short_qualified'] = short_qualified
    get_chunks(df)
    # filtered_df = df[(df['long_qualified']) | (df['short_qualified'])]
    filtered_df = df[(df['long_qualified'])]
    # filtered_df.to_csv(qualifying_trades_fn, index=False)
    # print('Qualifying Trades Data Exported!', qualifying_trades_fn)
    return filtered_df

def get_ref_chunks():
    hd = read_local_hd(hd_dl_fn)
    qualifying_trades = get_qualifying_trades(hd)
    ref_chunks_df = pd.DataFrame()
    ts = list(qualifying_trades['time'])
    ref_chunks_lst = list(qualifying_trades['raw_chunks'])
    ref_chunks_df['ts'] = ts
    ref_chunks_df['ref_chunks'] = ref_chunks_lst
    ref_chunks_df.to_csv(f'{downloads_path}\\ref_chunks.csv', index=False)
    print(f'Referance Chunks  Exported! {downloads_path}\\ref_chunks.csv')
    return ref_chunks_df

def get_tst_chunks():
    hd = read_local_hd(hd_dl_fn)
    close_pc_df = get_pc(hd)
    hd['close_pc'] = list(close_pc_df['pc'])
    chunks_df = get_chunks(hd)
    tst_chunks_df = pd.DataFrame()
    tst_chunks_df['ts'] = list(chunks_df['time'])
    tst_chunks_df['tst_chunks'] = list(chunks_df['raw_chunks'])
    tst_chunks_df.to_csv(f'{downloads_path}\\tst_chunks.csv', index=False)
    print(f'tst Chunks Exported! {downloads_path}\\tst_chunks.csv')
    return tst_chunks_df

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
    percent_dissimilarity = [abs(round((tst_lst_chunk[idx]*100/ref_lst_chunk[idx])-100, 4)) for idx in range(len(ref_lst_chunk))]
    avg = round(sum(percent_dissimilarity)/len(percent_dissimilarity), 4)
    return avg

def measure_dissimilarity(ref_chunks_lst_dict, tst_chunks_lst_dict):
    r= []
    qualified_tst_ts_lst = []
    qualified_avg_dissimilarity_lst = []
    start_ts = time()
    tot = len(ref_chunks_lst_dict)
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
                if avg_dissimilarity <= dissimilarity_threshold:
                    qualified_tst_ts_lst.append(tst_val['ts'])
                    qualified_avg_dissimilarity_lst.append(avg_dissimilarity)

        pattern_occurrence = len(qualified_avg_dissimilarity_lst)
        if pattern_occurrence >= min_pattern_occurrence:
            avg_avg_dissimilarity = round(sum(qualified_avg_dissimilarity_lst)/pattern_occurrence, 4)
            r.append({
                'avg_avg_dissimilarity': avg_avg_dissimilarity,
                'pattern_occurrence': pattern_occurrence,
                'ref_ts': ref_val['ts'],
                'qualified_tst_ts_lst': qualified_tst_ts_lst,
                'qualified_avg_dissimilarity_lst': qualified_avg_dissimilarity_lst,
            })
        qualified_tst_ts_lst = []
        qualified_avg_dissimilarity_lst = []
    print('\nExporting dissimilarity.csv')
    dissimilarity_df = pd.DataFrame(r)
    dissimilarity_df.to_csv(f'{downloads_path}\\dissimilarity.csv', index=False)
    print('dissimilarity.csv Exported!')
    return dissimilarity_df

config = get_config('config.json')
candlestick = config['candlestick']
chunk_size = config['chunk_size']
roi_threshold = config['roi_threshold']
sm_threshold = config['sm_threshold']
min_pattern_occurrence = config['min_pattern_occurrence']
dissimilarity_threshold = config['dissimilarity_threshold']

ref_chunks_df = get_ref_chunks()
ref_chunks_lst_dict = ref_chunks_df.to_dict(orient='records')
tst_chunks_df = get_tst_chunks()
tst_chunks_lst_dict = tst_chunks_df.to_dict(orient='records')

dissimilarity = measure_dissimilarity(ref_chunks_lst_dict, tst_chunks_lst_dict)