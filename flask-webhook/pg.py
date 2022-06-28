import pandas as pd
from os import listdir
from os.path import isfile, join




def calc_compounded_pnl(pnls):
    try:
        s=100.0
        for i in pnls:
            s = (1+(i/100))*s
        return round(s - 100.0,1)
    except:
        return 0

def prof_pct(pnls):
    try:
        only_pos = [num for num in pnls if num > 0]
        only_neg = [num for num in pnls if num < 0]
        pos_count = len(only_pos)
        neg_count = len(only_neg)
        return round(pos_count*100/(pos_count + neg_count), 1)
    except:
        return 0

def get_stats():
    logs_path='logs/'
    fns = [f'logs/{f}' for f in listdir(logs_path) if isfile(join(logs_path, f))]
    r = []
    for fn in fns:
        df = pd.read_csv(fn)
        pnls = list(df['PnL'])
        compounded_pnl = calc_compounded_pnl(pnls)
        profitable_trades_pct = prof_pct(pnls)
        s = fn.replace('logs/', '')
        strategy = s.replace('.csv', '')
        r.append({'strategy': strategy, 'compounded_pnl': compounded_pnl, 'profitable_trades_pct': profitable_trades_pct})
    return r

df = pd.DataFrame(get_stats())
df.to_html(classes='table table-stripped')
print(df)
