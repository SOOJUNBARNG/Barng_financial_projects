# 高速計算
import datetime

# データ操作ライブラリ
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

import numpy as np

#ターゲットには複数銘柄も指定可能です
target = "GOOGL"

target_list = ["GOOGL", "META", "NVDA", "SPRT"]

def calculate_ema(data, N):
    alpha = 2 / (N + 1)  # 平滑化係数
    ema = np.zeros(len(data))
    ema[0] = data.iloc[0]  # 最初の値はそのまま
    
    for i in range(1, len(data)):
        ema[i] = alpha * data.iloc[i] + (1 - alpha) * ema[i - 1]
    
    return ema

# 5日間のデータ取得 (日足)
data = yf.download(target, period='5d', interval="1d")

# EMA計算 (Close価格に対して適用)
ema_5 = calculate_ema(data["Close"], 5)

# 計算結果をデータフレームに追加
data["EMA_5"] = ema_5

# 表示
print(data)

# グラフ描画
plt.figure(figsize=(10, 5))
plt.plot(data.index, data["Close"], label="Close Price", marker="o")
plt.plot(data.index, data["EMA_5"], label="EMA 5", linestyle="dashed")
plt.legend()
plt.title(f"{target} - Close Price & EMA 5")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid()
plt.show()
