from flask import Flask, render_template, request, flash, redirect, jsonify, json, send_file
from binance.client import Client
from binance.enums import *
from time import time
import pickle as pickle
from datetime import datetime
import pandas as pd
from os import listdir
from os.path import isfile, join
import unicorn_binance_websocket_api
import threading
# from pushbullet import Pushbullet


app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

UTC_OFFSET = 14400000

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

def write_dictionary_to_file(dictionary, fn):
    try:
        old_val = read_dictionary_from_file(fn)
        for k in dictionary:
            old_val[k] = dictionary[k]
        with open(fn, 'w') as file:
            for key, value in old_val.items():
                file.write(f"{key}: {value}\n")
        print("Dictionary successfully written to position_logs.txt.")
    except Exception as e:
        print(f"Failed to write dictionary to file: {e}")

def get_client():
    fn = '/home/azureuser/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()

def get_open_position():
    # Retrieve account information
    account_info = client.futures_account()
    last_order_side = read_dictionary_from_file('position_logs.txt')['side']

    for val in account_info['positions']:
        if float(val['entryPrice']) != 0.0:
            return last_order_side

    return None


def get_entry_price(order_id):
    try:
        order = client.futures_get_order(symbol='BTCUSDT', orderId=order_id)
        entry_price = float(order['avgPrice'])
        return entry_price
    except Exception as e:
        print(f"Failed to retrieve entry price: {e}")
        return None


def create_tp_order():
    last_order = read_dictionary_from_file('position_logs.txt')
    last_order_entry_price = get_entry_price(last_order['order_id'])
    config = read_dictionary_from_file('config.txt')
    tp1 = float(config['tp1'])
    qty = float(config['qty'])
    leverage = int(config['leverage'])
    if last_order['side'] == 'BUY':
        tp1_price = int(last_order_entry_price*(1+(tp1/100)))

        new_side = 'SELL'
    if last_order['side'] == 'SELL':
        tp1_price = int(last_order_entry_price*(1-(tp1/100)))

        new_side = 'BUY'
    execute_limit_order(new_side, 'BTCUSDT', round(qty, 3), tp1_price)
    print(last_order_entry_price)


def execute_limit_order(side, symbol, quantity, price):
    config = read_dictionary_from_file('config.txt')
    leverage = int(config['leverage'])
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side.upper(),
            type='LIMIT',
            timeInForce='GTC',  # Good 'til Cancelled
            quantity=quantity,
            price=price,
            leverage=leverage
        )
        print(f"Limit order executed: {side} {quantity} {symbol} at price {price}. Order ID: {order['orderId']}")
        return order
    except Exception as e:
        print(f"Failed to execute limit order: {e}")
        return None


def execute_market_order(side, symbol, quantity):
    config = read_dictionary_from_file('config.txt')
    leverage = int(config['leverage'])
    try:
        order = client.futures_create_order(symbol=symbol, side=side.upper(), type='MARKET', quantity=quantity, leverage=leverage)
        write_dictionary_to_file({'side': side.upper(), 'order_id': order['orderId']}, 'position_logs.txt')
        print(f"Order executed: {side} {quantity} {symbol} at market price. Order ID: {order['orderId']}")
        return order
    except Exception as e:
        print(f"Failed to execute order: {e}")
        return None


def cancel_all_orders():
    try:
        open_orders = client.futures_get_open_orders()
        for order in open_orders:
            order_id = order['orderId']
            client.futures_cancel_order(symbol='BTCUSDT', orderId=order_id)
            print(f"Order {order_id} cancelled.")
    except Exception as e:
        print(f"Failed to cancel orders: {e}")

def close_all_positions():
    new_side = 'BUY' if read_dictionary_from_file('position_logs.txt')['side'] == 'SELL' else 'SELL'
    print(new_side)
    # Retrieve account information
    account_info = client.futures_account()

    # Get a list of open positions
    open_positions = [position for position in account_info['positions'] if float(position['entryPrice']) != 0.0]

    for i in open_positions:
        # print(new_side, i['symbol'], float(abs(i['positionAmt'])))
        execute_market_order(new_side, i['symbol'], abs(float(i['positionAmt'])))
    cancel_all_orders()


def get_local_time():
    UTC_OFFSET = 14400
    ts = int(time())
    lt = datetime.utcfromtimestamp(ts+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
    return lt


def update_csv(fn, val):
    with open(fn, "a") as myfile:
        myfile.write(val)

def get_last_pos(fn):
    try:
        df = pd.read_csv(f'logs/{fn}.csv')
        pos = list(df['Signal'])
        return pos[-1]
    except:
        return ''

def get_client():
    fn = '/home/azureuser/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])


client = get_client()


def get_price(coin):
    coin = f'{coin}USDT'
    all_prices = client.futures_symbol_ticker()
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



@app.route('/log_alert', methods=['POST'])  
def log_alert():
    local_time = get_local_time()
    price = get_price('BTC')
    print('Price is: ', price)
    ts = int(time())
    strat_id = request.json['strat_id']
    try:
        Final_longCondition = request.json["Final_longCondition"]
        L_first_condt_and_ACT_BT = request.json["L_first_condt_and_ACT_BT"]
        Final_shortCondition = request.json["Final_shortCondition"]
        S_first_condt_and_ACT_BT = request.json["S_first_condt_and_ACT_BT"]
        Final_Long_tp_and_not_Final_Long_tp2 = request.json["Final_Long_tp_and_not_Final_Long_tp2"]
        Final_Short_tp_and_not_Final_Short_tp2 = request.json["Final_Short_tp_and_not_Final_Short_tp2"]
        Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3 = request.json["Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3"]
        Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3 = request.json["Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3"]
        Final_Long_tp3_and_not_Final_Long_tp2 = request.json["Final_Long_tp3_and_not_Final_Long_tp2"]
        Final_Short_tp3_and_not_Final_Short_tp2 = request.json["Final_Short_tp3_and_not_Final_Short_tp2"]
        longSLhit = request.json["longSLhit"]
        shortSLhit = request.json["shortSLhit"]

        last_pos = get_last_pos(strat_id)
        conds = [Final_longCondition, L_first_condt_and_ACT_BT, Final_shortCondition, S_first_condt_and_ACT_BT, Final_Long_tp_and_not_Final_Long_tp2, Final_Short_tp_and_not_Final_Short_tp2, Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3, Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3, Final_Long_tp3_and_not_Final_Long_tp2, Final_Short_tp3_and_not_Final_Short_tp2, longSLhit, shortSLhit]


        if any(conds):
            sigs = []
            open_pos = get_open_position()
            if Final_longCondition or L_first_condt_and_ACT_BT:
                if(open_pos == None) or (open_pos == 'SELL'):
                    qty = float(read_dictionary_from_file('config.txt')['qty'])
                    close_all_positions()
                    execute_market_order('buy', 'BTCUSDT', qty)
                    create_tp_order()                    
                sigs.append('L')
                print('Alart: Long')
            if Final_shortCondition or S_first_condt_and_ACT_BT:
                if(open_pos == None) or (open_pos == 'BUY'):
                    qty = float(read_dictionary_from_file('config.txt')['qty'])
                    close_all_positions()
                    execute_market_order('sell', 'BTCUSDT', qty)
                    create_tp_order()                    
                sigs.append('S')
                print('Alart: Short')
            # if Final_Long_tp_and_not_Final_Long_tp2:
            #     sigs.append('L-TP1')
            # if Final_Short_tp_and_not_Final_Short_tp2:
            #     sigs.append('S-TP1')
            # if Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3:
            #     sigs.append('L-TP2')
            # if Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3:
            #     sigs.append('S-TP2')
            # if Final_Long_tp3_and_not_Final_Long_tp2:
            #     sigs.append('L-TP3')
            # if Final_Short_tp3_and_not_Final_Short_tp2:
            #     sigs.append('S-TP3')
            if longSLhit:
                if get_open_position()!= None:
                    close_all_positions()
                sigs.append('L-SL')
                print('L-SL')
            if shortSLhit:
                if get_open_position()!= None:
                    close_all_positions()
                sigs.append('S-SL')
                print('S-SL')

            for sig in sigs:
                if last_pos != sig:
                    data = f'{sig},{local_time},{price}\n'
                    fn = f'logs/{strat_id}.csv'
                    update_csv(fn, data)
                    data2 = f'{local_time},{Final_longCondition},{L_first_condt_and_ACT_BT},{Final_shortCondition},{S_first_condt_and_ACT_BT},{Final_Long_tp_and_not_Final_Long_tp2},{Final_Short_tp_and_not_Final_Short_tp2},{Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3},{Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3},{Final_Long_tp3_and_not_Final_Long_tp2},{Final_Short_tp3_and_not_Final_Short_tp2},{longSLhit},{shortSLhit}'


        data2 = f'{local_time},{Final_longCondition},{L_first_condt_and_ACT_BT},{Final_shortCondition},{S_first_condt_and_ACT_BT},{Final_Long_tp_and_not_Final_Long_tp2},{Final_Short_tp_and_not_Final_Short_tp2},{Final_Long_tp2_and_not_Final_Long_tp_and_not_Final_Long_tp3},{Final_Short_tp2_and_not_Final_Short_tp_and_not_Final_Short_tp3},{Final_Long_tp3_and_not_Final_Long_tp2},{Final_Short_tp3_and_not_Final_Short_tp2},{longSLhit},{shortSLhit}\n'            
        fn2 = f'logs/raw.csv'
        update_csv(fn2, data2)

    except Exception as e:
        fn2 = f'txt/{strat_id}.txt'
        data = f'{local_time}---{str(e)}\n'
        update_csv(fn2, data)
    return {}



@app.route('/s')
def stats():
    stats = pd.DataFrame(get_stats())
    return render_template('stats.html', tables=[stats.to_html()], titles=[''])

if __name__=="__main__":
    app.run(debug=False, host='0.0.0.0', port=80)
    # app.run(debug=True)
