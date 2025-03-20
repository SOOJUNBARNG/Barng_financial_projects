import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# ターゲット銘柄
target = "GOOGL"
n = 22  # 最高値・最安値の期間
atr_period = 22  # ATRの計算期間
multiplier = 3  # ATRの倍率

# データ取得 (過去3ヶ月分の日足データ)
data = yf.download(target, period="3mo", interval="1d")

# ATR 計算
def calculate_atr(df, period):
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift(1))
    low_close = np.abs(df["Low"] - df["Close"].shift(1))
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()  # 単純移動平均
    return atr

data["ATR"] = calculate_atr(data, atr_period)

# Chandelier Exit 計算
data["Chandelier_Long"] = data["High"].rolling(window=n).max().squeeze()  - multiplier * data["ATR"]
data["Chandelier_Short"] = data["Low"].rolling(window=n).min().squeeze()  + multiplier * data["ATR"]

# # 結果表示
# print(data[["Close", "Chandelier_Long", "Chandelier_Short"]])

# グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(data.index, data["Close"], label="Close Price", color="black")
plt.plot(data.index, data["Chandelier_Long"], label="Chandelier Exit Long", linestyle="dashed", color="blue")
plt.plot(data.index, data["Chandelier_Short"], label="Chandelier Exit Short", linestyle="dashed", color="red")
plt.legend()
plt.title(f"{target} - Chandelier Exit Strategy")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()
