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
 
def get_m_direction(dta):
    return [-1*int(i) for i in dta]


downloads_path = str(Path.home() / "Downloads")
tv_exp_fn = f'{downloads_path}\\BINANCE_BTCUSDTPERP, 3.csv'


tv_df = pd.read_csv(tv_exp_fn)
open_price = list(tv_df['open'])
high_price = list(tv_df['high'])
low_price = list(tv_df['low'])
close_price = list(tv_df['close'])


# Trend EMA HMA///////////////////////////////////////////////////////////////////////////
tradetrendoption = False
len111 = 200
m_src111 = close_price
m_out111 = ta.ema(tv_df['close'], len111)
m_mabuy = get_mabuy(m_out111)
m_masell = get_masell(m_out111)

# 5 EMAs HMA///////////////////////////////////////////////////////////////////////////
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

# SupertrendHMA///////////////////////////////////////////////////////////////////////////
atrPeriod = 10
factor = 3
supertrend_df = ta.supertrend(tv_df['high'], tv_df['low'], tv_df['close'], length=atrPeriod, multiplier=factor)
m_supertrend = list(supertrend_df['SUPERT_10_3.0'])
m_direction = get_m_direction(list(supertrend_df['SUPERTd_10_3.0']))

# HMA///////////////////////////////////////////////////////////////////////////
len6 = 100
src6 = close_price
m_hma = ta.wma(2*ta.wma(tv_df['close'], len6/2) - ta.wma(tv_df['close'], len6), float(np.floor(np.sqrt(len6))))

# Parabolic SAR/////////////////////////////////////////////////////////////////
start = 0.02
increment = 0.01
maximum = 0.2
# m_psr = ta.psar(high=tv_df['high'], low=tv_df['low'], af0=start, af=increment, max_af=maximum)

# RSI Divergence////////////////////////////////////////////////////////////////
len11 = 14
src11 = tv_df['close']
lbR11 = 2
lbL11 = 6
rangeUpper11 = 60
rangeLower11 = 5
plotBull11 = True
plotHiddenBull11 = False
plotBear11 = True
plotHiddenBear11 = False
m_osc11 = ta.rsi(src11, len11)
# plFound11 = na(pivotlow(osc11, lbL11, lbR11)) ? false : true

exp_df = pd.DataFrame()
exp_df['open'] = open_price
exp_df['high'] = high_price
exp_df['low'] = low_price
exp_df['close'] = close_price
exp_df['pivotlow'] = list(tv_df['pivotlow'])
exp_df['m_osc11'] = m_osc11

exp_fn = 'exp_df.csv'
exp_df.to_csv(exp_fn, index=False)
os.system(f"start EXCEL.EXE {exp_fn}")
