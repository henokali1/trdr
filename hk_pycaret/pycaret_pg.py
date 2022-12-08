import pandas as pd

downloads_path = str(Path.home() / "Downloads")

raw_data = pd.read_csv(f'{downloads_path}1-BTCUSDT-5min.csv')

