import pandas as pd
from time import sleep

def calc_long_pnl(entry_price, exit_price):
    try:
        return round((exit_price*100/entry_price)-100.0, 2)
    except:
        return 0.0

def str_to_csv(val):
    with open("long_exp.csv", "w") as file1:
        file1.writelines(val)


fn = '1-BTCUSDT-5min.csv'

df=pd.read_csv(fn)

start_ts = 1620691200000 # Date and time (GMT): Tuesday, May 11, 2021 12:00:00 AM
end_ts = 1633910400000 # Date and time (GMT): Monday, October 11, 2021 12:00:00 AM


ts = list(df["0"])
open_p = list(df["1"])
high_p = list(df["2"])
low_p = list(df["3"])
close_p = list(df["4"])

start_idx = ts.index(start_ts)
end_idx = ts.index(end_ts)

title = 'ts,L1,L2,L3,L4,L5,L6,L7,L8,L9,L10,L11,L12,L13,L14,L15,L16,L17,L18,L19,L20,L21,L22,L23,L24,L25,L26,L27,L28,L29,L30,L31,L32,L33,L34,L35,L36,L37,L38,L39,L40,L41,L42,L43,L44,L45,L46,L47,L48,L49,L50\n'

# tst_chunk = ts[start_idx:end_idx]
tst_chunk = ts[51:-51]
tot = len(tst_chunk)
cntr = 0
for cur_ts in tst_chunk:
    cntr += 1
    remaining = tot - cntr
    cur_ts_idx = ts.index(cur_ts)
    a = f'{ts[cur_ts_idx]}'
    for i in range(50):
        long_pnl = calc_long_pnl(high_p[cur_ts_idx], high_p[cur_ts_idx + 1 + i])
        a += f',{long_pnl}'
    a += '\n'
    title += a
    if cntr%1000 == 0:
        p_rem = round((cntr*100/tot), 2)
        p = f'Cntr: {cntr}      \t      Remaining: {remaining}      \t      {p_rem} % completed'+' '*15
        print(f'\r{p}', end='')


str_to_csv(title)
