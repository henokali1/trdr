import matplotlib.pylab as plt
import os



from tsfresh import extract_features, extract_relevant_features, select_features
from tsfresh.utilities.dataframe_functions import impute

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

import pandas as pd
import numpy as np

df = pd.read_csv(os.path.abspath('../data/df.csv'))
y = pd.read_csv(os.path.abspath('../data/y.csv'))

df["id"] = df.index
df = df.melt(id_vars="id", var_name="time").sort_values(["id", "time"]).reset_index(drop=True)
X = extract_features(df[df["id"] < len(df)], column_id="id", column_sort="time", impute_function=impute)
X.to_csv(os.path.abspath('../data/X.csv'), index=False)
