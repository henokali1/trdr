import os
import numpy as np
import pandas as pd
import pandas_ta as ta
from pathlib import Path
from datetime import datetime


downloads_path = str(Path.home() / "Downloads")
tv_exp_fn = f'{downloads_path}\\BINANCE_BTCUSDT.P, 15.csv'
tv_exp_fn = f'{downloads_path}\\tst.csv'

N = 4
per = 144
mult = 1.414
modeLag = False
modeFast = False
beta = 0.00503274062721631
alpha = 0.0954202818890498
lag = 17.875