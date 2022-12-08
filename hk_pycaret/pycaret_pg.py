import pandas as pd
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")

raw_data = pd.read_csv(f'{downloads_path}\\1-BTCUSDT-5min.csv')

raw_ts = list(raw_data['0'])
open_price = list(raw_data['1'])
high_price = list(raw_data['2'])
low_price = list(raw_data['3'])
close_price = list(raw_data['4'])
vol = list(raw_data['7'])

close_price_ratio = [0.0]
vol_ratio = [0.0]
raw_idx = [0]

TS = []
CPR1=[]
CPR2=[]
CPR3=[]
CPR4=[]
CPR5=[]
CPR6=[]
VR1=[]
VR2=[]
VR3=[]
VR4=[]
VR5=[]
VR6=[]

for idx in range(len(close_price)):
    if idx > 0:
        raw_idx.append(idx)
        try:
            close_price_ratio.append(close_price[idx]/close_price[idx-1])
            vol_ratio.append(vol[idx]/vol[idx-1])
        except:
            vol_ratio.append(0.0)

for idx in range(len(raw_ts)):
    if idx >= 6:
        TS.append(raw_ts[idx])
        CPR1.append(close_price_ratio[idx-1])
        CPR2.append(close_price_ratio[idx-2])
        CPR3.append(close_price_ratio[idx-3])
        CPR4.append(close_price_ratio[idx-4])
        CPR5.append(close_price_ratio[idx-5])
        CPR6.append(close_price_ratio[idx-6])
        VR1.append(vol_ratio[idx-1])
        VR2.append(vol_ratio[idx-2])
        VR3.append(vol_ratio[idx-3])
        VR4.append(vol_ratio[idx-4])
        VR5.append(vol_ratio[idx-5])
        VR6.append(vol_ratio[idx-6])

exp_df = pd.DataFrame()
exp_df['TS'] = TS
exp_df['CPR1']=CPR1
exp_df['CPR2']=CPR2
exp_df['CPR3']=CPR3
exp_df['CPR4']=CPR4
exp_df['CPR5']=CPR5
exp_df['CPR6']=CPR6
exp_df['VR1']=VR1
exp_df['VR2']=VR2
exp_df['VR3']=VR3
exp_df['VR4']=VR4
exp_df['VR5']=VR5
exp_df['VR6']=VR6

print(raw_data.head())
print(exp_df.head())
