import unicorn_binance_websocket_api
import json
import time

import datetime
from datetime import datetime
import datetime as dt

binance_websocket_api_manager = unicorn_binance_websocket_api.BinanceWebSocketApiManager(exchange="binance.com-futures")
binance_websocket_api_manager.create_stream(['aggTrade'], ['btcusdt'])
UTC_OFFSET = 14400

while True:
    stream = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
    if stream:
        jsonstream = json.loads(stream)
        res = jsonstream.get('data') 
        if res:
            lts = int(time.time())+UTC_OFFSET
            ltm = datetime.utcfromtimestamp(lts).strftime('%d-%m-%Y %H:%M:%S')
            pair = res['s']
            current_price = float(res['p'])
            fm = f'{ltm}\tPair: {pair}\tPrice: {current_price}\t\t'
            print(f"\r{fm}",end="")
