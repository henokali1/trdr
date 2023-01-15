import pandas as pd
from pycaret.datasets import get_data
from pycaret.classification import *
from pathlib import Path
from os import system

downloads_path = str(Path.home() / "Downloads")

dataset = pd.read_csv(f'{downloads_path}\\training_dataset.csv')
data = dataset.sample(frac=0.9, random_state=786).reset_index(drop=True)
data_unseen = dataset.drop(data.index).reset_index(drop=True)
print('Data for Modeling: ' + str(data.shape))
print('Unseen Data For Predictions: ' + str(data_unseen.shape))
exp_mclf101 = setup(data = data, target = 'LABEL', session_id=123, use_gpu=True) 
compare_models()
dt = create_model('gbc')
tuned_dt = tune_model(dt)
evaluate_model(tuned_dt)
predict_model(tuned_dt)
final_dt = finalize_model(tuned_dt)
plot_model(tuned_dt, plot = 'confusion_matrix')
unseen_predictions = predict_model(tuned_dt, data=data_unseen)
unseen_predictions.head()
save_model(final_dt,'Final gbc Model 10Dec2022')
print(final_dt)
"""

# saved_final_dt = load_model('Final DT Model 12Dec2022')
# new_prediction = predict_model(saved_final_dt, data=data_unseen)
# new_prediction.head()
"""
