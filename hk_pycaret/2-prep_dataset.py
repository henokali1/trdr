import pandas as pd
from pathlib import Path
from os import system


downloads_path = str(Path.home() / "Downloads")

df = pd.read_csv(f'{downloads_path}\\processed.csv')
training_df = pd.DataFrame()

training_df['CPR1']=df['CPR1']
training_df['CPR2']=df['CPR2']
training_df['CPR3']=df['CPR3']
training_df['CPR4']=df['CPR4']
training_df['CPR5']=df['CPR5']
training_df['CPR6']=df['CPR6']
training_df['VR1']=df['VR1']
training_df['VR2']=df['VR2']
training_df['VR3']=df['VR3']
training_df['VR4']=df['VR4']
training_df['VR5']=df['VR5']
training_df['VR6']=df['VR6']
training_df['LABEL']=df['LABEL']

exp_fn = f'{downloads_path}\\training_dataset.csv'
training_df.to_csv(exp_fn, index=False)
system(f"start EXCEL.EXE {exp_fn}")
