from flask import Flask, render_template, request, flash, redirect, jsonify, json, send_file
from binance.client import Client
from binance.enums import *
from time import time
import pickle as pickle
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

def read_db():
    with open('db.pickle', 'rb') as handle:
        val = pickle.load(handle)
    return val

def write_to_db(val):
    with open('db.pickle', 'wb') as handle:
        pickle.dump(val, handle, protocol=pickle.HIGHEST_PROTOCOL)

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

def get_client():
    fn = '/home/henokali1/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()


def get_balance(coin):
    account = client.get_account()
    balances = account['balances']
    for balance in balances:
        if balance['asset'] == coin:
            return float(balance['free'])
    return None

def get_price(coin):
    coin = f'{coin}USDT'
    all_prices = client.get_all_tickers()
    for pair in all_prices:
        if pair['symbol'] == coin:
            return float(pair['price'])
    return None


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
        r.append({'strategy': strategy, 'c_PnL': f'{compounded_pnl}%', 'PTP': f'{profitable_trades_pct}%'})
    return r


def get_btc_24hr_price_change_percent():
    OFFSET_1MIN = 60000
    OFFSET_24HR = 86400000
    try:
        ts = int(time())*1000
        cur_start = ts - OFFSET_1MIN
        cur_end = ts
        yest_start = ts - OFFSET_24HR - OFFSET_1MIN
        yest_end = ts - OFFSET_24HR
        openPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(yest_start), str(yest_end))[0][1])
        lastPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(cur_start), str(cur_end))[0][1])
        priceChangePercent = (lastPrice - openPrice )/(openPrice)*100
        return round(priceChangePercent, 2)
    except:
        return 0.0


@app.route('/webhook', methods=['POST']) 
def webhook():
    pnl = 0
    # print(request.json['bs'])
    asset = request.json['asset']
    price = get_price(asset)
    local_time = get_local_time()
    ts = int(time())
    pos = request.json['type']
    strat_id = request.json['strat_id']
    last_pos = get_last_pos(strat_id)
    btc_24hr_pc = get_btc_24hr_price_change_percent()
    if last_pos != pos:
        fn = f'logs/{strat_id}.csv'
        if (last_pos == 'es' and pos == 'xl') or (last_pos == 'el' and pos == 'xs'):
            return {'d':'d'}
        if (last_pos == 'xs' and pos == 'xl') or (last_pos == 'xl' and pos == 'xs'):
            return {'d':'d'}
        if (last_pos == 'el' and pos == 'xl') or (last_pos == 'el' and pos == 'es'):
            try:
                entry_price = get_last_entry_price(fn)
                pnl = round((price*100/entry_price)-100.0, 2)
            except:
                pnl = 0
        if (last_pos == 'es' and pos == 'xs') or (last_pos == 'es' and pos == 'el'):
            try:
                entry_price = get_last_entry_price(fn)
                pnl = round((entry_price*100/price)-100.0, 2)
            except:
                pnl = 0
        data = f'{local_time},{pos},{asset},{price},{ts},{btc_24hr_pc},{pnl}\n'
        update_csv(fn, data)
    
    
    # Create Order
    # if ((bs == 'EL') and (position == 'N')):
    #     client.futures_change_leverage(symbol='BTCUSDT', leverage=leverage)
    #     to = client.futures_create_order(symbol='BTCUSDT', type='MARKET', side='BUY', quantity=0.008)
    #     position = 'B'
    #     print(to)
    #     log = f'Entry Long - {str(to)}'
    #     logger.critical(log)

    # if ((bs == 'XL') and (position == 'B')):
    #     client.futures_change_leverage(symbol='BTCUSDT', leverage=leverage)
    #     to = client.futures_create_order(symbol='BTCUSDT', type='MARKET', side='SELL', quantity=0.008)
    #     position = 'N'
    #     print(to)
    #     log = f'Exit Long - {str(to)}'
    #     logger.critical(log)

    # if ((bs == 'ES') and (position == 'N')):
    #     client.futures_change_leverage(symbol='BTCUSDT', leverage=leverage)
    #     to = client.futures_create_order(symbol='BTCUSDT', type='MARKET', side='SELL', quantity=0.008)
    #     position = 'S'
    #     print(to)
    #     log = f'Entry Short - {str(to)}'
    #     logger.critical(log)

    # if ((bs == 'XS') and (position == 'S')):
    #     client.futures_change_leverage(symbol='BTCUSDT', leverage=leverage)
    #     to = client.futures_create_order(symbol='BTCUSDT', type='MARKET', side='BUY', quantity=0.008)
    #     position = 'N'
    #     print(to)
    #     log = f'Exit Short - {str(to)}'
    #     logger.critical(log)
    return {'d':'d'}


@app.route('/log')
def downloadFile():
    path = "/home/ubuntu/TRDR/zigZag-PA-futures-alert-from-tradingview/trade.log"
    return send_file(path, as_attachment=True)


@app.route('/s')
def stats():
    stats = pd.DataFrame(get_stats())
    return render_template('stats.html', tables=[stats.to_html()], titles=[''])

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
    # app.run(debug=True)
