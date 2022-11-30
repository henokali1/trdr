import os
import numpy as np
import pandas as pd
import pandas_ta as ta
from pathlib import Path

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
src111 = tv_df
m_out111 = ta.ema(tv_df['close'], len111)
# ma111  = plot(out111, title="EMA 200", linewidth=2, color=color.blue, offset=0)
# mabuy  = out111 > out111[1]
# masell = out111 < out111[1]

exp_df = pd.DataFrame()
exp_df['open'] = open_price
exp_df['high'] = high_price
exp_df['low'] = low_price
exp_df['close'] = close_price
exp_df['out111'] = list(tv_df['out111'])
exp_df['m_out111'] = m_out111

exp_fn = 'exp_df.csv'
exp_df.to_csv(exp_fn, index=False)
os.system(f"start EXCEL.EXE {exp_fn}")
