from threading import current_thread
from flask import Flask, render_template, request, flash, redirect, jsonify, json, send_file
from time import time
from datetime import datetime
import pandas as pd
from os import listdir
from os.path import isfile, join
# from pushbullet import Pushbullet


app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

UTC_OFFSET = 14400000
TRADE_SYMBOL = 'BUSDUSDT'
TRADE_QUANTITY = 99.5
BUSD_TRADE_PERCENTAGE = 99.5
SELL_PERCENTAGE = 99.5

trade_percentage = BUSD_TRADE_PERCENTAGE/100.0
sell_trade_percentage = SELL_PERCENTAGE/100.0

leverage = 5
caps = [100.0]
position = 'N'

def get_local_time():
    UTC_OFFSET = 14400
    ts = int(time())
    lt = datetime.utcfromtimestamp(ts+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
    return lt

def update_csv(fn, val):
    with open(fn, "a") as myfile:
        myfile.write(val)

def read_logs():
    with open("trade.log") as file:
        data = file.read()
    return data

def get_last_pos(fn):
    try:
        df = pd.read_csv(f'logs/{fn}.csv')
        pos = list(df['pos'])
        return pos[-1]
    except:
        return ''

def get_last_entry_price(fn):
    try:
        df = pd.read_csv(fn)
        last_price = list(df['price'])
        return float(last_price[-1])
    except:
        return 0.0

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

def get_days_cnt():
    start_date_ts = 1653788703
    one_day_secs = 86400
    current_date_ts = int(time())
    days = int((current_date_ts - start_date_ts) / one_day_secs)
    return days

def get_avg_c_pnl(c_pnls):
    return round(sum(c_pnls)/len(c_pnls),1)

def get_vmc_pnls():
    vmc_pnls_raw = list(pd.read_csv('/home/henokali1/trdr/vmc/log.csv')['Profit'])
    vmc_pnls = []
    for i in vmc_pnls_raw:
        if i != 'NAN':
            vmc_pnls.append(float(i))
    return vmc_pnls

def get_stats():
    logs_path='/home/henokali1/trdr/flask-webhook/logs'
    fns = [f'{logs_path}/{f}' for f in listdir(logs_path) if isfile(join(logs_path, f))]
    c_pnls = []
    r = []
    for fn in fns:
        print(fn)
        df = pd.read_csv(fn)
        pnls = list(df['PnL'])
        compounded_pnl = calc_compounded_pnl(pnls)
        c_pnls.append(compounded_pnl)
        profitable_trades_pct = prof_pct(pnls)
        s = fn.replace('/home/henokali1/trdr/flask-webhook/logs/', '')
        strategy = s.replace('.csv', '')
        r.append({'strategy': strategy, 'c_PnL': f'{compounded_pnl}%', 'PTP': f'{profitable_trades_pct}%'})
    # --------------------------------------------------------------- VMC ----------------------------------------------------------------
    vmc_pnls = get_vmc_pnls()
    vmc_compounded_pnl = calc_compounded_pnl(vmc_pnls)
    c_pnls.append(vmc_compounded_pnl)
    vmc_profitable_trades_pct = prof_pct(vmc_pnls)
    r.append({'strategy': 'VMC_MHD', 'c_PnL': f'{vmc_compounded_pnl}%', 'PTP': f'{vmc_profitable_trades_pct}%'})
    # --------------------------------------------------------------- VMC ----------------------------------------------------------------
    avg_c_pnl = get_avg_c_pnl(c_pnls)    
    return r,avg_c_pnl

def get_trade_logs(strat):
    logs_path=f'/home/henokali1/trdr/flask-webhook/logs/{strat}.csv'
    df = pd.read_csv(logs_path)
    return df

@app.route('/d')
def downloadFile():
    strat = request.args.get('strat')
    fn=f'/home/henokali1/trdr/flask-webhook/logs/{strat}.csv'
    return send_file(fn, as_attachment=True)


@app.route('/s')
def stats():
    stats,avg_c_pnl = get_stats()
    days = get_days_cnt()
    return render_template('stats.html', stats=stats, days=days, avg_c_pnl=avg_c_pnl)

@app.route('/trade_log')
def trade_log():
    s = request.args.get('strat')
    stats = get_trade_logs(s)
    log=pd.DataFrame(stats).iloc[::-1]
    pnls = list(log['PnL'])
    compounded_pnl = calc_compounded_pnl(pnls)
    profitable_trades_pct = prof_pct(pnls)
    return render_template('logs.html', strat=s.replace('_', ' '), tables=[log.to_html()], titles=[''], compounded_pnl=compounded_pnl, profitable_trades_pct=profitable_trades_pct, pnls=pnls)

@app.route('/vmc_log')
def vmc_log():
    logs_path = '/home/henokali1/trdr/vmc/log.csv'
    log = pd.read_csv(logs_path).iloc[::-1]
    # log=pd.DataFrame(df).iloc[::-1]
    return render_template('vmc-logs.html', tables=[log.to_html()], titles=[''])

@app.route('/vmc_dl')
def vmc_dl():
    fn=f'/home/henokali1/trdr/vmc/log.csv'
    return send_file(fn, as_attachment=True)


if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=9999)
    # app.run(debug=True)
