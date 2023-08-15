from binance.client import Client
from binance.enums import *
from time import time
import pickle as pickle
from datetime import datetime
from os import listdir
from os.path import isfile, join
import unicorn_binance_websocket_api
import threading
import ast
import pandas as pd

def get_client():
    fn = '/home/azureuser/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()


def get_unix_timestamp(date_string):
    """
    Converts the input date string to Unix timestamp.

    Parameters:
        date_string (str): Input date string in the format "dd/mm/yyyy hh:mm:ss".

    Returns:
        int: Unix timestamp of the given date.
    """
    try:
        date_obj = datetime.strptime(date_string, "%d/%m/%Y %H:%M:%S")
        timestamp = int(date_obj.timestamp())
        return timestamp
    except ValueError:
        print("Invalid date format. Please use the format 'dd/mm/yyyy hh:mm:ss'.")
        return None


def heikin_ashi(df):
    """
    Converts the input DataFrame into Heikin Ashi candles and returns it as a new DataFrame.

    Parameters:
        df (pandas.DataFrame): Input DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume'].

    Returns:
        pandas.DataFrame: DataFrame with Heikin Ashi candles and columns ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
    """
    ha_df = pd.DataFrame(index=df.index, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'real_open'])
    tot = len(df)
    for i in range(tot):
        if i == 0:
            ha_df.iloc[i] = df.iloc[i]
        else:
            ha_df.at[i, 'time'] = df.at[i, 'time']
            ha_df.at[i, 'open'] = (ha_df.at[i - 1, 'open'] + ha_df.at[i - 1, 'close']) / 2
            ha_df.at[i, 'close'] = (df.at[i, 'open'] + df.at[i, 'high'] + df.at[i, 'low'] + df.at[i, 'close']) / 4
            ha_df.at[i, 'high'] = max(df.at[i, 'high'], ha_df.at[i, 'open'], ha_df.at[i, 'close'])
            ha_df.at[i, 'low'] = min(df.at[i, 'low'], ha_df.at[i, 'open'], ha_df.at[i, 'close'])
            ha_df.at[i, 'volume'] = df.at[i, 'volume']
            ha_df.at[i, 'real_open'] = df.at[i, 'real_open']

    return ha_df

def get_historical_data(start_timestamp, end_timestamp): 
    data = []
    tot = (end_timestamp - start_timestamp)/(900*500)
    cntr = 0
    for current_sts in range(start_timestamp, end_timestamp+1, 900*500):
        next_ets = current_sts + 900*500 if (current_sts + 900*500) < end_timestamp else end_timestamp
        print(current_sts, next_ets, f'100% completed') if next_ets == end_timestamp else print(current_sts, next_ets, f'{round(cntr*100/tot, 1)}% completed')
        cntr += 1
        klines = client.futures_historical_klines('BTCUSDT', '15m', current_sts*1000, next_ets*1000, limit=500)
        
        for kline in klines:
            timestamp = kline[0]/1000
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            data.append([timestamp, open_price, high_price, low_price, close_price, volume, open_price])
    print('Converting to Heikin Ashi...')

    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'real_open'])
    # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # hdf = heikin_ashi(df)
    hdf = df
    # hdf.to_csv(f'{start_timestamp}--{end_timestamp}.csv', index=False)
    hdf.to_csv(f'tst.csv', index=False)
    print('Data Exported')


start_timestamp = get_unix_timestamp('01/10/2019 00:00:00')
end_timestamp = int(time())


get_historical_data(start_timestamp, end_timestamp)

