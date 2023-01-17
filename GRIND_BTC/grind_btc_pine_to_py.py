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
                ret.append(1 if (low_price[idx-4] > low_price[idx-2] and low_price[idx-3] >= low_price[idx-2] and low_price[idx-2] <= low_price[idx-1] and low_price[idx-2] < low_price[idx-0]) else 0)
            else:
                ret.append(0)
        else:
            ret.append(0)
    return ret

def get_TrendDirection():
    r = [(-1 if m_fastEMA[i] < m_mediumEMA[i] and m_pacU[i] < m_mediumEMA[i] else
          1 if m_fastEMA[i] > m_mediumEMA[i] and m_pacL[i] > m_mediumEMA[i] else
          0) for i in range(len(m_fastEMA))]
    return r

def valuewhen(condition, source, occurrence):
    prev = [None]*(occurrence+1)
    r=[]
    for idx,val in enumerate(condition):
        if val:
            prev.append(source[idx])
        r.append(prev[-1*(occurrence+1)])
    return r

def get_higherhigh():
    r=[]
    for idx,val in enumerate(m_filteredtopf):
        try:
            if val == 0:
                r.append(0)
            else:
                r.append(1 if m_valuewhen_H1[idx] < m_valuewhen_H0[idx] and m_valuewhen_H2[idx] < m_valuewhen_H0[idx] else 0)
        except:
            r.append(0)
    return r

def get_lowerhigh():
    r=[]
    for idx,val in enumerate(m_filteredtopf):
        try:
            if val == 0:
                r.append(0)
            else:
                r.append(1 if m_valuewhen_H1[idx] > m_valuewhen_H0[idx] and m_valuewhen_H2[idx] > m_valuewhen_H0[idx] else 0)
        except:
            r.append(0)
    return r

def get_higherlow():
    r=[]
    for idx,val in enumerate(m_filteredbotf):
        try:
            if val == 0:
                r.append(0)
            else:
                r.append(1 if m_valuewhen_L1[idx] < m_valuewhen_L0[idx] and m_valuewhen_L2[idx] < m_valuewhen_L0[idx] else 0)
        except:
            r.append(0)
    return r

def get_lowerlow():
    r=[]
    for idx,val in enumerate(m_filteredbotf):
        try:
            if val == 0:
                r.append(0)
            else:
                r.append(1 if m_valuewhen_L1[idx] > m_valuewhen_L0[idx] and m_valuewhen_L2[idx] > m_valuewhen_L0[idx] else 0)
        except:
            r.append(0)
    return r

def barssince(condition):
    cntr=0
    cnt = False
    r=[]
    for idx,val in enumerate(condition):
        if (idx > 1) and (condition[idx-1] == 1 ) and (val == 0):
            cnt = True
        if (idx > 1) and (condition[idx-1] == 0 ) and (val == 1):
            cntr = 0
            cnt = False
        if cnt:
            cntr += 1
        r.append(cntr)
    return r



tv_df = pd.read_csv(tv_exp_fn)
os.remove(tv_exp_fn)
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

m_fastEMA = ta.ema(tv_df['close'], fastEMAlength)
m_mediumEMA = ta.ema(tv_df['close'], mediumEMAlength)
m_slowEMA = ta.ema(tv_df['close'], slowEMAlength)
m_pacC = ta.ema(tv_df['close'], HiLoLen)
m_pacL = ta.ema(tv_df['low'], HiLoLen)
m_pacU = ta.ema(tv_df['high'], HiLoLen)
m_TrendDirection = get_TrendDirection()
m_filteredtopf = get_isBWFractal(1)
m_filteredbotf = get_isBWFractal(-1)
m_valuewhen_H0 = valuewhen(m_filteredtopf, [None, None]+high_price[:-2], 0)
m_valuewhen_H1 = valuewhen(m_filteredtopf, [None, None]+high_price[:-2], 1)
m_valuewhen_H2 = valuewhen(m_filteredtopf, [None, None]+high_price[:-2], 2)
m_higherhigh = get_higherhigh()
m_lowerhigh = get_lowerhigh()
m_valuewhen_L0 = valuewhen(m_filteredbotf, [None, None]+low_price[:-2], 0)
m_valuewhen_L1 = valuewhen(m_filteredbotf, [None, None]+low_price[:-2], 1)
m_valuewhen_L2 = valuewhen(m_filteredbotf, [None, None]+low_price[:-2], 2)
m_higherlow = get_higherlow()
m_lowerlow = get_lowerlow()
m_barssince_haClose_lt_pacC = barssince([1 if haClose[i]<m_pacC[i] else 0 for i in range(len(haClose))])
m_barssince_haClose_gt_pacC = barssince([1 if haClose[i]>m_pacC[i] else 0 for i in range(len(haClose))])
m_pacExitU = [1 if(haOpen[i] < m_pacU[i] and haClose[i] > m_pacU[i] and m_barssince_haClose_lt_pacC[i] <= Lookback) else 0 for i in range(len(m_barssince_haClose_lt_pacC))]
m_pacExitL = [1 if(haOpen[i] > m_pacL[i] and haClose[i] < m_pacL[i] and m_barssince_haClose_gt_pacC[i] <= Lookback) else 0 for i in range(len(m_barssince_haClose_gt_pacC))]
tv_TrendDirection = list(tv_df['TrendDirection'])
m_Buy = [1 if(tv_TrendDirection[i] == 1 and m_pacExitU[i]) else 0 for i in range(len(tv_TrendDirection))]
m_Sell = [1 if(tv_TrendDirection[i] == -1 and m_pacExitL[i]) else 0 for i in range(len(tv_TrendDirection))]

exp_df = pd.DataFrame()
exp_df['open'] = open_price
exp_df['high'] = high_price
exp_df['low'] = low_price
exp_df['close'] = close_price
exp_df['Sell'] = list(tv_df['Sell'])
exp_df['m_Sell'] = m_Sell

exp_fn = f'{downloads_path}\\exp_df.csv'
exp_df.to_csv(exp_fn, index=False)
os.system(f"start EXCEL.EXE {exp_fn}")
