import os
import numpy as np
import pandas as pd
import pandas_ta as ta
from pathlib import Path


def get_mabuy(m_out111):
    r=[0]
    for idx in range(len(m_out111)):
        if idx > 0:
            r.append(int(m_out111[idx] > m_out111[idx-1]))
    return r

def get_masell(m_out111):
    r=[0]
    for idx in range(len(m_out111)):
        if idx > 0:
            r.append(int(m_out111[idx] < m_out111[idx-1]))
    return r
 


downloads_path = str(Path.home() / "Downloads")
tv_exp_fn = f'{downloads_path}\\BINANCE_BTCUSDTPERP, 3.csv'


tv_df = pd.read_csv(tv_exp_fn)
open_price = list(tv_df['open'])
high_price = list(tv_df['high'])
low_price = list(tv_df['low'])
close_price = list(tv_df['close'])


# Trend EMA
tradetrendoption = False
len111 = 200
m_src111 = close_price
m_out111 = ta.ema(tv_df['close'], len111)
m_mabuy = get_mabuy(m_out111)
m_masell = get_masell(m_out111)

# 5 EMAs
len1 = 9
len2 = 21
len3 = 55
len4 = 100
len5 = 200
m_src1 = close_price
m_src2 = close_price
m_src3 = close_price
m_src4 = close_price
m_src5 = close_price
m_out1 = ta.ema(tv_df['close'], len1)
m_out2 = ta.ema(tv_df['close'], len2)
m_out3 = ta.ema(tv_df['close'], len3)
m_out4 = ta.ema(tv_df['close'], len4)
m_out5 = ta.ema(tv_df['close'], len5)

# Supertrend
atrPeriod = 10
factor = 3
supertrend_df = ta.supertrend(tv_df['high'], tv_df['low'], tv_df['close'], length=atrPeriod, multiplier=factor)
m_supertrend = list(supertrend_df['SUPERT_10_3.0'])
m_direction = list(supertrend_df['SUPERTd_10_3.0'])

exp_df = pd.DataFrame()
exp_df['open'] = open_price
exp_df['high'] = high_price
exp_df['low'] = low_price
exp_df['close'] = close_price
exp_df['direction'] = list(tv_df['direction'])
exp_df['m_direction'] = m_direction

exp_fn = 'exp_df.csv'
exp_df.to_csv(exp_fn, index=False)
os.system(f"start EXCEL.EXE {exp_fn}")
