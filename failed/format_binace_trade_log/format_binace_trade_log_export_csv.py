import pandas as pd
from os import remove
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")

def read_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return [line.strip() for line in lines]

def save_list_to_file(filename, lst):
    with open(filename, 'w') as f:
        for item in lst:
            f.write("%s\n" % item)

def clean_data(fn):
    raw = read_file(fn)
    raw_cleaned = []
    title = raw.pop(0)
    for i in raw:
        sp = i.split(',')
        if not ((sp[5]  == '') or ('Entry' in sp[1])):
            raw_cleaned.append(i)

    inv = [title] + raw_cleaned[::-1]
    save_list_to_file('d.csv', inv)


    df = pd.read_csv('d.csv')
    remove('d.csv')
    trade_num = list(df['Trade #'])
    trade_type = list(df['Type'])
    signal = list(df['Signal'])
    dt = list(df['Date/Time'])
    price = list(df['Price USDT'])
    profit_percent = list(df['Profit %'])

    cleaned_df = pd.DataFrame()

    cleaned_df['Trade #'] = trade_num
    cleaned_df['Type'] = trade_type
    cleaned_df['Signal'] = signal
    cleaned_df['Date/Time'] = dt
    cleaned_df['Price USDT'] = price
    cleaned_df['Profit %'] = profit_percent
    cleaned_df.to_csv(f'{downloads_path}/cleaned.csv', index=False)

fn = f'{downloads_path}/Alart_My_GRIND_BTC_[15MIN]_List_of_Trades_2023-05-27.csv'
clean_data(fn)

uniuqe = ['L-TP1', 'TP1-TP2', 'TP2-TP3', 'S-TP1', 'TP3-L', 'TP1-L', 'TP3-S', 'TP2-L', 'TP2-S', 'L-S', 'TP1-S', 'S-L', 'TP3-TP1']
