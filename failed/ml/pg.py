import pandas as pd
import numpy as np
import pandas_ta as ta
from pycaret.classification import load_model, predict_model
from pycaret.classification import *
from pycaret.classification import ClassificationExperiment
from sklearn.ensemble import ExtraTreesClassifier


def get_class(val):
    ranges = {(0, 0.5): '0-0.5', (0.5, 1.0): '0.5-1.0', (1.0, 1.5): '1.0-1.5', (1.5, 2.0): '1.5-2.0', (2.0, 2.5): '2.0-2.5', (2.5, 3.0): '2.5-3.0', (3.0, 3.5): '3.0-3.5', (3.5, 4.0): '3.5-4.0', (4.0, 4.5): '4.0-4.5', (4.5, 5.0): '4.5-5.0', (5.0, 5.5): '5.0-5.5', (5.5, 6.0): '5.5-6.0', (6.0, 6.5): '6.0-6.5', (6.5, 7.0): '6.5-7.0', (7.0, 7.5): '7.0-7.5', (7.5, 8.0): '7.5-8.0', (8.0, 8.5): '8.0-8.5', (8.5, 9.0): '8.5-9.0', (9.0, 9.5): '9.0-9.5', (9.5, 10.0): '9.5-10.0', (10, float('inf')): 'gt-10', (-float('inf'), -10): 'lt--10', (-10, -9.5): '-10--9.5', (-9.5, -9.0): '-9.5--9.0', (-9.0, -8.5): '-9.0--8.5', (-8.5, -8.0): '-8.5--8.0', (-8.0, -7.5): '-8.0--7.5', (-7.5, -7.0): '-7.5--7.0', (-7.0, -6.5): '-7.0--6.5', (-6.5, -6.0): '-6.5--6.0', (-6.0, -5.5): '-6.0--5.5', (-5.5, -5.0): '-5.5--5.0', (-5.0, -4.5): '-5.0--4.5', (-4.5, -4.0): '-4.5--4.0', (-4.0, -3.5): '-4.0--3.5', (-3.5, -3.0): '-3.5--3.0', (-3.0, -2.5): '-3.0--2.5', (-2.5, -2.0): '-2.5--2.0', (-2.0, -1.5): '-2.0--1.5', (-1.5, -1.0): '-1.5--1.0', (-1.0, -0.5): '-1.0--0.5', (-0.5, 0.0): '-0.5-0.0'}
    for key, value in ranges.items():
        if key[0] <= val < key[1]:
            return value

    return 'uk'

def generate_features(df, coin_pair, fn):
    candlestick_frame = 12
    pnl_threshold = 3


    try:
        df.ta.strategy("all")
        # 2/0
    except Exception as e:
        print(e)
        ts = list(df['time'])
        open = list(df['open'])
        high = list(df['high'])
        low = list(df['low'])
        close = list(df['close'])
        volume = list(df['volume'])
        tot = len(ts)
        long_runup_lst = []
        long_drawdown_lst = []
        short_runup_lst = []
        short_drawdown_lst = []
        pnls = []
        signal = []

        for idx in range(tot):
            if (idx >= candlestick_frame) and (idx <= tot - candlestick_frame-1):
                pnl = round((open[idx+candlestick_frame]*100/open[idx+1])-100, 2)
                pnls.append(pnl)
                signal.append(get_class(pnl))
            else:
                pnls.append('uk')
                signal.append('uk')
                   
        
        # df['pnl'] = pnls
        df['signal'] = signal

        df = df.drop(columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'DPO_20', 'HILOl_13_21', 'ICS_26', 'PSARl_0.02_0.2', 'QQEl_14_5_4.236', 'SUPERTl_7_3.0'], axis=1)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        dataset_fn = f'../../data/{fn}.csv'
        df.to_csv(dataset_fn, index=False)
        print(f'{coin_pair} Features Generated and saved')
        return df

def train_model(data):
    exp = ClassificationExperiment()

    s = setup(data, target = 'signal', session_id = 123, use_gpu=True)
    # model = compare_models(exclude=['gbc'])
    # model = create_model(DecisionTreeClassifier())
    model = create_model(ExtraTreesClassifier())

    # save pipeline
    model_name = 'model_ta_feats'
    save_model(model, f'../../models/{model_name}')
    plot_model(model, plot = 'confusion_matrix', plot_kwargs = {'percent': True}, save=True)
    plot_model(model, plot = 'feature_all', save=True)


def validate_model(data):
    model_name = f'model_ta_feats'
    model = load_model(f'/home/hk_sc/models/{model_name}')

    correct_signals = list(data['signal'])
    predictions = predict_model(model, data)

    exp_df = pd.DataFrame()
    exp_df['prediction_score'] = predictions['prediction_score']
    exp_df['correct_signals'] = correct_signals
    exp_df['prediction_label'] = predictions['prediction_label']
    exp_df.to_csv('/home/hk_sc/data/predictions.csv', index=False)
    print('-'*100)
    print('-'*100)
    print('-'*42, 'VALIDATON DONE', '-'*42)
    print('-'*100)
    print('-'*100)

    
raw_df = pd.read_csv('../../data/BTCUSDT_testing_2023.csv')
generate_features(raw_df, 'BTCUSDT', 'ta_testing_feats')

data = pd.read_csv('/home/hk_sc/data/ta_testing_feats.csv')
validate_model(data)

