# データ操作
import pandas as pd

# 時間周りライブラリ
from datetime import datetime

# 本番ライブラリ
from elliottwaves_barng import ElliottWaveFindPattern

# 時間データ
today = pd.to_datetime(datetime.today()).strftime('%Y-%m-%d')

# Load your data into a pandas DataFrame
df = pd.read_csv('./input_data/4188_mitsubishi.csv')
# the dataset
df["Date"] = pd.to_datetime(df["time"], errors="coerce")
df.set_index("Date")
# print(df_source.head(5))


# Call the function
ElliottWaveFindPattern(df, 'close', 30 , '2013-01-04', today)
print(ElliottWaveFindPattern)


