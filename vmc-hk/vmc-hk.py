# from signal import *
import numpy as np
import pandas as pd 

import time
import ccxt
from binance.client import Client
import datetime
import os.path 
from finta import TA
import datetime as dt
import pickle
import requests



def read_pickle_file(fn):
    with open(fn, 'rb') as handle:
        val = pickle.load(handle)
    print('read_pickle_file')
    return val

def get_client():
    fn = '/home/henokali1/key/binance-key.pickle'
    with open(fn, 'rb') as handle:
        k = pickle.load(handle)
    return Client(k['API_KEY'], k['API_SECRET'])

def get_historical_data(client, coin_pair, start_ts, end_ts):
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # 1h = KLINE_INTERVAL_1HOUR 
    # 30m = KLINE_INTERVAL_30MINUTE
    # returns OHLCV
    return client.get_historical_klines(coin_pair, Client.KLINE_INTERVAL_1HOUR, start_ts, end_ts)

def get_btc_24hr_price_change_percent():
    ts = int(time.time())*1000
    cur_start = ts - OFFSET_1MIN
    cur_end = ts
    yest_start = ts - OFFSET_24HR - OFFSET_1MIN
    yest_end = ts - OFFSET_24HR
    openPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(yest_start), str(yest_end))[0][1])
    lastPrice = float(client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, str(cur_start), str(cur_end))[0][1])
    priceChangePercent = (lastPrice - openPrice )/(openPrice)*100
    return round(priceChangePercent, 2)

def get_signal():
    btc_24hr_pc = get_btc_24hr_price_change_percent()
    print('btc_24hr_pc', btc_24hr_pc)
    end_ts = int(time.time())*1000
    start_ts = end_ts - 2591999000
    for idx, pair in enumerate(pairs_list):
        print(f'{idx}: working on {pair}')
        d = get_historical_data(client, pair, start_ts, end_ts)
        df = pd.DataFrame(d)
        df.columns = ['unix_ts', 'open', 'high', 'low', 'close', 'Volume', 'close time', 'Quote asset' 'volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']

        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        wt_df=TA.WTO(df,14,21)
        df['wt1'] = wt_df['WT1.']
        df['wt2'] = wt_df['WT2.']

        df['previous_wt1'] = df['wt1'].shift(1)
        df['previous_wt2'] = df['wt2'].shift(1)
        df['crossing_down'] = (df['wt1'] <= df['wt2']) & (df['previous_wt1'] >= df['previous_wt2']) & (df['wt2'] >= WT_OVERBOUGHT )
        df['crossing_up'] = (df['wt1'] >= df['wt2']) & (df['previous_wt1'] <= df['previous_wt2']) & (df['wt2'] <= WT_OVERSOLD )
        df['signal']=np.where(df['crossing_up'] , 'long', (np.where(df['crossing_down'], 'short', 'no_sig')))
        sig = list(df['signal'])[-1]
        if (btc_24hr_pc > LONG_ENTRY_THRESHOLD) and (sig == 'long'):
            return {'asset': pair[:-4], 'pos': 'el'}
        if (btc_24hr_pc < SHORT_ENTRY_THRESHOLD) and (sig == 'short'):
            return {'asset': pair[:-4], 'pos': 'es'}
    return None

def send_alert(asset, pos):
    url = 'http://localhost/webhook'
    alert = {"type": pos, "strat_id": "VMC_HK", "asset": asset}
    r = requests.post(url, json=alert)
    print('r', r)
    print('status', r.status_code)

# CONSTANTS
pairs_list = ['SOLUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'TRXUSDT', 'LTCUSDT', 'APEUSDT', 'AVAXUSDT', 'LINKUSDT', 'LITUSDT', 'GMTUSDT', 'DOTUSDT', 'FTMUSDT', 'GALAUSDT', 'SHIBUSDT', 'NEARUSDT', 'MATICUSDT', 'PEOPLEUSDT', 'SANDUSDT', 'MANAUSDT', 'VETUSDT', 'ATOMUSDT', 'LUNAUSDT', 'WAVESUSDT', 'JASMYUSDT', 'ENSUSDT', 'BCHUSDT', 'EGLDUSDT', 'RUNEUSDT', 'ETCUSDT', 'ZILUSDT', 'UNFIUSDT', 'FILUSDT', 'ALICEUSDT', 'AAVEUSDT', 'OPUSDT', 'ALGOUSDT', 'OGNUSDT', 'EOSUSDT', 'XLMUSDT', 'ICPUSDT', 'THETAUSDT', 'AXSUSDT', 'XMRUSDT', 'HNTUSDT', 'WOOUSDT', 'UNIUSDT', 'CHZUSDT', 'ROSEUSDT', 'SRMUSDT', 'TFUELUSDT', 'GALUSDT', 'STORJUSDT', 'FTTUSDT', 'ZECUSDT', 'ANCUSDT', 'LRCUSDT', 'API3USDT', 'BATUSDT', 'TWTUSDT', 'CAKEUSDT', 'BELUSDT', 'DYDXUSDT', 'GRTUSDT', 'RSRUSDT', 'FLMUSDT', 'CRVUSDT', 'ONEUSDT', 'BLZUSDT', 'QNTUSDT', 'POLSUSDT', 'XTZUSDT', 'JSTUSDT', 'GLMRUSDT', 'SUSHIUSDT', 'IMXUSDT', 'MASKUSDT', 'ARUSDT', 'NEOUSDT', 'SLPUSDT', 'CHRUSDT', 'ANTUSDT', 'DARUSDT', 'BNXUSDT', 'BTTCUSDT', 'WINUSDT', 'ONTUSDT', 'CELOUSDT', 'KNCUSDT', 'HBARUSDT', 'ENJUSDT', 'HOTUSDT', 'BAKEUSDT', 'IOTXUSDT', 'KDAUSDT', 'PONDUSDT', 'CITYUSDT', 'DUSKUSDT', 'IOTAUSDT', 'IOSTUSDT', 'DASHUSDT', 'MINAUSDT', 'SFPUSDT', 'MBLUSDT', 'SUNUSDT', 'TOMOUSDT', 'RVNUSDT', 'COMPUSDT', 'KLAYUSDT', 'GTCUSDT', 'MKRUSDT', 'SXPUSDT', 'QTUMUSDT', 'FETUSDT', 'KAVAUSDT', 'DENTUSDT', 'TCTUSDT', 'OMGUSDT', 'ATAUSDT', 'YFIUSDT', 'CELRUSDT', 'ANKRUSDT', 'FLOWUSDT', 'ZRXUSDT', 'LINAUSDT', 'LOKAUSDT', 'CTKUSDT', 'TLMUSDT', 'KP3RUSDT', 'COTIUSDT', 'C98USDT', 'KSMUSDT', 'AUDIOUSDT', 'ASTRUSDT', 'ZENUSDT', 'YFIIUSDT', 'WINGUSDT', 'POWRUSDT', 'CVXUSDT', 'QIUSDT', 'SPELLUSDT', 'UMAUSDT', 'OCEANUSDT', '1INCHUSDT', 'DODOUSDT', 'SNXUSDT', 'RENUSDT', 'NKNUSDT', 'REEFUSDT', 'BICOUSDT', 'BSWUSDT', 'BURGERUSDT', 'CTSIUSDT', 'BETAUSDT', 'PYRUSDT', 'MTLUSDT', 'ASRUSDT', 'PERPUSDT', 'TRBUSDT', 'STMXUSDT', 'ALPINEUSDT', 'MBOXUSDT', 'MOVRUSDT', 'BNTUSDT', 'XECUSDT', 'LDOUSDT', 'CTXCUSDT', 'RLCUSDT', 'BANDUSDT', 'IDEXUSDT', 'ARPAUSDT', 'YGGUSDT', 'POLYUSDT', 'ICXUSDT', 'EPXUSDT', 'SANTOSUSDT', 'AVAUSDT', 'RNDRUSDT', 'MIRUSDT', 'SKLUSDT', 'REPUSDT', 'ADXUSDT', 'OGUSDT', 'TROYUSDT', 'NEXOUSDT', 'TUSDT', 'NULSUSDT', 'SYSUSDT', 'AGLDUSDT', 'INJUSDT', 'VOXELUSDT', 'COCOSUSDT', 'WAXPUSDT', 'ACAUSDT', 'STXUSDT', 'LAZIOUSDT', 'DGBUSDT', 'XVSUSDT', 'SCRTUSDT', 'LPTUSDT', 'WRXUSDT', 'ILVUSDT', 'HIVEUSDT', 'RAYUSDT', 'PSGUSDT', 'CKBUSDT', 'CVCUSDT', 'BARUSDT', 'ELFUSDT', 'CFXUSDT', 'ALPHAUSDT', 'REQUSDT', 'COSUSDT', 'SCUSDT', 'FISUSDT', 'STPTUSDT', 'KEYUSDT', 'AUTOUSDT', 'PORTOUSDT', 'PLAUSDT', 'XNOUSDT', 'SUPERUSDT', 'QUICKUSDT', 'GTOUSDT', 'BIFIUSDT', 'ALCXUSDT', 'AKROUSDT', 'DIAUSDT', 'VGXUSDT', 'ORNUSDT', 'ATMUSDT', 'WNXMUSDT', 'XEMUSDT', 'FLUXUSDT', 'TORNUSDT', 'STRAXUSDT', 'FORUSDT', 'ACHUSDT', 'MITHUSDT', 'ALPACAUSDT', 'DREPUSDT', 'TRIBEUSDT', 'OOKIUSDT', 'XVGUSDT', 'ACMUSDT', 'MFTUSDT', 'STEEMUSDT', 'MULTIUSDT', 'RAMPUSDT', 'HIGHUSDT', 'UTKUSDT', 'BALUSDT', 'MDTUSDT', 'FARMUSDT', 'JUVUSDT', 'BTSUSDT', 'PUNDIXUSDT', 'DEGOUSDT', 'BTCSTUSDT', 'OXTUSDT', 'CLVUSDT', 'ERNUSDT', 'BTGUSDT', 'BEAMUSDT', 'TKOUSDT', 'MCUSDT', 'LTOUSDT', 'ONGUSDT', 'FORTHUSDT', 'RIFUSDT', 'RAREUSDT', 'DATAUSDT', 'MLNUSDT', 'TRUUSDT', 'FRONTUSDT', 'MDXUSDT', 'VIDTUSDT', 'REIUSDT', 'JOEUSDT', 'GNOUSDT', 'AMPUSDT', 'TVKUSDT', 'BADGERUSDT', 'CHESSUSDT', 'FIDAUSDT', 'VTHOUSDT', 'AUCTIONUSDT', 'WTCUSDT', 'AUCTIONUSDT', 'DOCKUSDT', 'DFUSDT', 'FIOUSDT', 'FIROUSDT', 'DNTUSDT', 'OMUSDT', 'MOBUSDT', 'LSKUSDT', 'WANUSDT', 'RADUSDT', 'PNTUSDT', 'NBSUSDT', 'BONDUSDT', 'AIONUSDT', 'PHAUSDT', 'GHSTUSDT', 'IRISUSDT', 'FUNUSDT', 'CVPUSDT', 'DEXEUSDT', 'KMDUSDT', 'PERLUSDT', 'NMRUSDT', 'VITEUSDT', 'DCRUSDT', 'ARDRUSDT', 'GBPUSDT', 'FXSUSDT', 'EURUSDT', 'AUDUSDT']
blacklist = ['GBPUSDT', 'FXSUSDT', 'EURUSDT', 'AUDUSDT']
# Remove black listed coins
for pair in blacklist:
    if pair in pairs_list:
        pairs_list.remove(pair)


print(f'Tracking {len(pairs_list)} Coins, {len(blacklist)} Blacklisted Coins')


OFFSET_30d = 2591999000
OFFSET_24HR = 86400000
OFFSET_1MIN = 60000
UTC_OFFSET = 14400
WT_OVERBOUGHT=35
WT_OVERSOLD=-35
LONG_ENTRY_THRESHOLD = 0.0
SHORT_ENTRY_THRESHOLD = 0.0




client = get_client() 
sig = get_signal()
print(sig)
if sig != None:
    asset = sig['asset']
    pos = sig['pos']
    send_alert(asset, pos)

# asset = 'BEAM'
# pos = 'xl'
# send_alert(asset, pos)
