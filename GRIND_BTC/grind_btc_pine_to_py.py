import os
import numpy as np
import pandas as pd
import pandas_ta as ta
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")
tv_exp_fn = f'{downloads_path}\\BINANCE_BTCUSDTPERP, 15.csv'

def get_hl2(high_price, low_price):
    r=[(high_price[i] + low_price[i])/2 for i in range(len(high_price))]
    return r

def get_src0(close_price):
    return [None] + close_price[:-1]

def get_isRegularFractal(mode):
    ret = []
    for idx in range(len(low_price)):
        if idx >= 4:
            if mode == 1:
                ret.append(1 if(high_price[idx-4] < high_price[idx-3] and high_price[idx-3] < high_price[idx-2] and high_price[idx-2] > high_price[idx-1] and high_price[idx-1] > high_price[idx-0]) else 0)
            elif mode == -1:
                ret.append(1 if (low_price[idx-4] > low_price[idx-3] and low_price[idx-3] > low_price[idx-2] and low_price[idx-2] < low_price[idx-1] and low_price[idx-1] < low_price[idx-0]) else 0)
            else:
                ret.append(0)
        else:
            ret.append(0)
    return ret

def get_isBWFractal(mode):
    ret = []
    for idx in range(len(low_price)):
        if idx >= 4:
            if mode == 1:
                ret.append(1 if (high_price[idx-4] < high_price[idx-2] and high_price[idx-3] <= high_price[idx-2] and high_price[idx-2] >= high_price[idx-1] and high_price[idx-2] > high_price[idx-0]) else 0)
            elif mode == -1:
                ret.appnd(1 if (low_price[idx-4] > low_price[idx-2] and low_price[idx-3] >= low_price[idx-2] and low_price[idx-2] <= low_price[idx-1] and low_price[idx-2] < low_price[idx-0]) else 0)
            else:
                ret.append(0)
        else:
            ret.append(0)
    return ret



tv_df = pd.read_csv(tv_exp_fn)
open_price = list(tv_df['open'])
high_price = list(tv_df['high'])
low_price = list(tv_df['low'])
close_price = list(tv_df['close'])

# SOURCE 
m_hl2 = get_hl2(high_price, low_price)

# INPUTS ========================================================================================================================================
# POSITION
is_Long = True
is_Short = True

# ADX
Act_ADX = True
ADX_options = 'MASANAKAMURA'
ADX_len = 9
th = 12

# RSI
len_3 = 100
src_3 = open_price

# Volume weight
maLength = 51
maType = 'SMA'
rvolTrigger = '1.3'

# TREND STRENGHT
n1 = 10
n2 = 21

# JMA
inp = close_price
reso = 'Chart'
rep = False
m_src0 = get_src0(close_price)
lengths = 50

# MACD
fast_length = 3
slow_length = 4
signal_length = 7

# MA
start = 0.011
increment = 0.006
maximum = 0.08
width = 1

# Volume Delta
periodMa = 5

# BACKTESTING ========================================================================================================================================
ACT_BT = True
long_ = True
short_ = True
risk = 100

# SCALPING ========================================================================================================================================
# Inputs
ACT_SCLP = True
HiLoLen = 24
fastEMAlength = 10
mediumEMAlength = 100
slowEMAlength = 500
filterBW = False
Lookback = 6
UseHAcandles = True

# Indicator
haClose = close_price
haOpen = open_price
haHigh = high_price
haLow = low_price

exp_df = pd.DataFrame()
exp_df['open'] = open_price
exp_df['high'] = high_price
exp_df['low'] = low_price
exp_df['close'] = close_price
exp_df['isBWFractal(1)'] = list(tv_df['isBWFractal(1)'])
exp_df['m_get_isBWFractal(1)'] = get_isBWFractal(1)

exp_fn = 'exp_df.csv'
exp_df.to_csv(exp_fn, index=False)
os.system(f"start EXCEL.EXE {exp_fn}")
