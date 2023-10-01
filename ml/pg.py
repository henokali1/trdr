import pandas as pd
from pycaret.classification import *
from pycaret.classification import ClassificationExperiment
from lightgbm import LGBMClassifier
import numpy as np

from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer


exp = ClassificationExperiment()
data = pd.read_csv('/home/hk_sc/data/ETHUSDT-dataset.csv')
coin = list(data['coin'])[0]
data['signal'].replace({'dont_trade': 0, 'long': 1, 'short': 2}, inplace=True)

data = data.select_dtypes(include=['number'])  # This keeps only numeric columns

# Separate the features (X) and the target variable (y)
X = data.drop(columns=['signal'])
y = data['signal']

# Handle missing values in X using SimpleImputer (replace NaN with the mean of each column)
imputer = SimpleImputer(strategy='mean')
X = imputer.fit_transform(X)

# Initialize the SMOTE object
smote = SMOTE(random_state=42)

# Apply SMOTE to balance the dataset
X_resampled, y_resampled = smote.fit_resample(X, y)

# Create a new balanced dataframe
data = pd.concat([pd.DataFrame(X_resampled, columns=data.columns[:-1]), pd.DataFrame({'signal': y_resampled})], axis=1)
# data.to_csv('/home/hk_sc/data/balanced_data.csv', index=False)
# data = pd.read_csv('/home/hk_sc/data/balanced_data.csv')

data.replace([np.inf, -np.inf], np.nan, inplace=True)
data['coin'] = [coin]*len(data['signal'])

s = setup(data, target = 'signal', categorical_features=['coin'], session_id = 123, use_gpu=True)
model = create_model(LGBMClassifier())
validation_scores = pull()

# save pipeline
save_model(model, f'/home/hk_sc/models/unbalanced_cpu')
plot_model(model, plot = 'confusion_matrix', plot_kwargs = {'percent': True}, save=True)
print('Training finished.............')
