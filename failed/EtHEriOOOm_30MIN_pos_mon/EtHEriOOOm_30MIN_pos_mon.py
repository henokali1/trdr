import pandas as pd 
import numpy as np
import time
from binance.client import Client
import datetime
from datetime import datetime
from finta import TA
import datetime as dt
import pickle
import requests
import asyncio
from binance import AsyncClient, BinanceSocketManager


UTC_OFFSET = 14400

def read_pickle_file(fn):
    with open(fn, 'rb') as handle:
        val = pickle.load(handle)
    print('read_pickle_file')
    return val

def get_ks():
    fn = '/home/henokali1/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return k




async def main():
    k=get_ks()
    client = await AsyncClient.create(api_key=k['API_KEY'], api_secret=k['API_SECRET'])
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket('ETHUSDT')
    # then start receiving messages
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            bts=res['E']
            # btm = datetime.utcfromtimestamp(int(bts)+UTC_OFFSET).strftime('%d-%m-%Y %H:%M:%S')
            lts = int(time.time())+UTC_OFFSET
            ltm = datetime.utcfromtimestamp(lts).strftime('%d-%m-%Y %H:%M:%S')
            pair = res['s']
            current_price = float(res['p'])
            fm = f'{ltm}\tPair: {pair}\tPrice: {current_price}\t\t'
            print(f"\r{fm}",end="")

    await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
