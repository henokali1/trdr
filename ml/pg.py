import pandas as pd
import numpy as np
import pandas_ta as ta
from pycaret.classification import load_model, predict_model



model_name = f'model_ta_feats'
model = load_model(f'/home/hk_sc/models/{model_name}')
plot_model(model, plot = 'confusion_matrix', plot_kwargs = {'percent': True}, save=True)

data = pd.read_csv('/home/hk_sc/data/ta_feats.csv')

correct_signals = list(data['signal'])
predictions = predict_model(model, data)

exp_df = pd.DataFrame()
exp_df['prediction_score'] = predictions['prediction_score']
exp_df['correct_signals'] = correct_signals
exp_df['signal'] = predictions['signal']
exp_df['prediction_label'] = predictions['prediction_label']
exp_df.to_csv('/home/hk_sc/data/predictions.csv')
