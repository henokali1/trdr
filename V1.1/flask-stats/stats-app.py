from threading import current_thread
from flask import Flask, render_template, request, flash, redirect, jsonify, json, send_file
from time import time
from datetime import datetime
import pandas as pd
from os import listdir
from os.path import isfile, join
import ast
from binance.client import Client
from binance.enums import *
import pickle

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



def convert_string_to_list(string):
    try:
        # Use ast.literal_eval to safely evaluate the string as a Python expression
        # and convert it into a list
        result = ast.literal_eval(string)
        if isinstance(result, list):
            return result
        else:
            raise ValueError("Invalid string format. Expected a string representing a list.")
    except (SyntaxError, ValueError) as e:
        print(f"Failed to convert string to list: {e}")
        return None


def read_dictionary_from_file(fn):
    try:
        with open(fn, 'r') as file:
            lines = file.readlines()

        dictionary = {}
        for line in lines:
            key, value = line.strip().split(': ')
            dictionary[key] = value

        return dictionary
    except Exception as e:
        print(f"Failed to read file and convert to dictionary: {e}")
        return None


def get_client():
    fn = '/home/azureuser/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()

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

def get_days_cnt(s):
    trade_logs = get_trade_logs(s)
    start_date_ts = int(list(trade_logs['ts'])[0])
    one_day_secs = 86400
    current_date_ts = int(time())
    days = int((current_date_ts - start_date_ts) / one_day_secs)
    return days

def get_avg_c_pnl(c_pnls):
    return round(sum(c_pnls)/len(c_pnls),1)

def get_stats():
    logs_path='/home/azureuser/trdr/flask-webhook/logs'
    fns = [f'{logs_path}/{f}' for f in listdir(logs_path) if isfile(join(logs_path, f))]
    c_pnls = []
    r = []
    win_to_loss_ratios = []
    for fn in fns:
        print(fn)
        df = pd.read_csv(fn)
        pnls = list(df['PnL'])
        compounded_pnl = calc_compounded_pnl(pnls)
        c_pnls.append(compounded_pnl)
        profitable_trades_pct = prof_pct(pnls)
        s = fn.replace('/home/azureuser/trdr/flask-webhook/logs/', '')
        strategy = s.replace('.csv', '')
        n_days = get_days_cnt(strategy)
        pnl_to_day_ratio = compounded_pnl if n_days == 0 else round(compounded_pnl/n_days, 1)
        r.append({'strategy': strategy, 'c_PnL': f'{compounded_pnl}%', 'PTP': f'{profitable_trades_pct}%', 'win_to_loss_ratio': get_win_to_loss_ratio(strategy), 'pnl_to_day_ratio': pnl_to_day_ratio})
   
    avg_c_pnl = get_avg_c_pnl(c_pnls)    
    return r,avg_c_pnl

def get_trade_logs(strat):
    logs_path=f'/home/azureuser/trdr/flask-webhook/logs/{strat}.csv'
    df = pd.read_csv(logs_path)
    return df

def get_format_logs(strat):
    df = get_trade_logs(strat)

    date_time = list(df['date-time'])
    pos = list(df['pos'])
    asset = list(df['Asset'])
    price = list(df['price'])
    unix_ts = list(df['ts'])
    pnl = list(df['PnL'])

    frmtd = []
    for idx, val in enumerate(pos):
        if 'x' in val:
            position = 'Long' if pos[idx-1] == 'el' else 'Short'
            frmtd.append({'PnL': pnl[idx], 'Pos': position, 'Asset': asset[idx], 'Entry Time': date_time[idx-1], 'Entry Price': price[idx-1], 'Exit Time': date_time[idx], 'Exit Price': price[idx]})
    return pd.DataFrame(frmtd).iloc[::-1]

def get_win_to_loss_ratio(strat):
    df = get_trade_logs(strat)
    pnl = list(df['PnL'])
    p=[]
    n=[]
    for i in pnl:
        if i > 0:
            p.append(i)
        if i < 0:
            n.append(i)
    try:
        return round(sum(p)/(-1 * sum(n)), 1)
    except:
        return 0.0

@app.route('/d')
def downloadFile():
    strat = request.args.get('strat')
    fn=f'/home/azureuser/trdr/flask-webhook/logs/{strat}.csv'
    return send_file(fn, as_attachment=True)


@app.route('/s')
def stats():
    stats,avg_c_pnl = get_stats()
    return render_template('stats.html', stats=stats, avg_c_pnl=avg_c_pnl)

@app.route('/over_view')
def over_view():
    stats,_ = get_stats()
    return jsonify(stats)

@app.route('/trade_log')
def trade_log():
    s = request.args.get('strat')
    stats = get_trade_logs(s)
    log=pd.DataFrame(stats).iloc[::-1]
    pnls = list(log['PnL'])
    compounded_pnl = calc_compounded_pnl(pnls)
    profitable_trades_pct = prof_pct(pnls)
    n_days = get_days_cnt(s)
    pnl_to_day_ratio = compounded_pnl if n_days == 0 else round(compounded_pnl/n_days, 1)
    return render_template('logs.html', strat=s.replace('_', ' '), tables=[log.to_html()], titles=[''], compounded_pnl=compounded_pnl, profitable_trades_pct=profitable_trades_pct, pnls=pnls, n_days=n_days, pnl_to_day_ratio=pnl_to_day_ratio)

@app.route('/strat_log')
def strat_log():
    s = request.args.get('strat')
    stats = get_trade_logs(s)
    log=pd.DataFrame(stats).iloc[::-1]
    pnls = list(log['PnL'])
    compounded_pnl = calc_compounded_pnl(pnls)
    profitable_trades_pct = prof_pct(pnls)
    n_days = get_days_cnt(s)
    pnl_to_day_ratio = compounded_pnl if n_days == 0 else round(compounded_pnl/n_days, 1)

    pos_lst = list(log['pos'])
    dt_lst = list(log['date-time'])
    asset_lst = list(log['Asset'])
    price_lst = list(log['price'])
    pnl_lst = list(log['PnL'])
    fd=[]
    for i in range(len(pos_lst)):
        fd.append({"pos": pos_lst[i], "date_time": dt_lst[i], "Asset": asset_lst[i], "price": price_lst[i], "PnL": pnl_lst[i]})
    data = {
        "fd": fd,
        "compounded_pnl": compounded_pnl,
        "profitable_trades_pct": profitable_trades_pct,
        "pnl_to_day_ratio": pnl_to_day_ratio,
        "strat": s,
        "n_days": n_days,
        "pnls": pnls,
    }
    return jsonify(data)

@app.route('/frmtd_log')
def frmtd_log():
    s = request.args.get('strat')
    stats = get_trade_logs(s)
    log=pd.DataFrame(stats).iloc[::-1]
    pnls = list(log['PnL'])
    compounded_pnl = calc_compounded_pnl(pnls)
    profitable_trades_pct = prof_pct(pnls)
    n_days = get_days_cnt(s)
    pnl_to_day_ratio = compounded_pnl if n_days == 0 else round(compounded_pnl/n_days, 1)
    format_logs = get_format_logs(s)
    win_to_loss_ratio = get_win_to_loss_ratio(s)
    return render_template('frmtd_log.html', strat=s.replace('_', ' '), tables=[format_logs.to_html()], titles=[''], compounded_pnl=compounded_pnl, profitable_trades_pct=profitable_trades_pct, pnls=pnls, n_days=n_days, pnl_to_day_ratio=pnl_to_day_ratio, win_to_loss_ratio=win_to_loss_ratio)


def get_futures_wallet_balance():
    try:
        account_info = client.futures_account()
        total_balance = float(account_info['totalWalletBalance'])
        return total_balance
    except Exception as e:
        print(f"Failed to retrieve futures wallet balance: {e}")
        return None

def calculate_net_pnl():
    try:
        balance = get_futures_wallet_balance()
        inital_capital = sum(convert_string_to_list(read_dictionary_from_file('/home/azureuser/trdr/flask-webhook/config.txt')['capital']))
        net_pnl = (balance*100/inital_capital)-100.0
        return round(net_pnl, 2)
    except Exception as e:
        print('Failed to calculate NET PNL: {e}')
        return None
    



@app.route('/view_trade_logs')
def view_trade_logs():
    s = request.args.get('strat')
    logs = get_trade_logs(s)[::-1]
    
    return render_template('tst.html', strat=s.replace('_', ' '), tables=[logs.to_html()], titles=[''], net_pnl=calculate_net_pnl())

@app.route('/tst')
def tst():
    s = request.args.get('strat')
    logs = get_trade_logs(s)
    
    return render_template('tst.html', strat=s.replace('_', ' '), tables=[logs.to_html()], titles=[''])


if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=9999)
    # app.run(debug=True)
