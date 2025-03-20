import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import yfinance as yf

ticker = "GOOGL"

tickers = ["1301.T"]
# tickers = ["GOOGL", "META", "NVDA", "TNXP", "CVNA", "FINV", "VITL"]
# not_tickers = ["JBSAY", ]

read_tickers_list = pd.read_csv("./yahoo_stocklist.csv")
read_tickers_list = read_tickers_list.rename(columns={
    "コード": "code",
    "銘柄名称": "name",
    "業種": "industry",
    "市場": "market",
    "取引所": "exchange",
})

# コードに".T"を追加
read_tickers_list["code"] = read_tickers_list["code"].astype(str) + ".T"


def calculate_ema(data, N):
    alpha = 2 / (N + 1)  # 平滑化係数
    ema = np.zeros(len(data))
    ema[0] = data.iloc[0]  # 最初の値はそのまま
    
    for i in range(1, len(data)):
        ema[i] = alpha * data.iloc[i] + (1 - alpha) * ema[i - 1]
    
    return ema

def calculate_atr(df, period):

    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift(1))
    low_close = np.abs(df["Low"] - df["Close"].shift(1))
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()  # 単純移動平均
    return atr


def calculate_ce(data, max_min_period, atr_period, multiplier):
    data["ATR"] = calculate_atr(data, atr_period)

    # Chandelier Exit 計算
    data["Chandelier_Long"] = data["High"].rolling(window=max_min_period).max().squeeze()  - multiplier * data["ATR"]
    data["Chandelier_Short"] = data["Low"].rolling(window=max_min_period).min().squeeze()  + multiplier * data["ATR"]

    return data

def gap(price1, price2):
    return abs(price1 - price2) / price2 

save_list = []
for index, row in read_tickers_list.iterrows():

    ticker = row["code"]
    name = row["name"]
    # data = yf.download(target, period='5d', interval="1d")
    # データ取得 (過去3ヶ月分の日足データ)
    try: 
        data = yf.download(ticker, period="10y", interval="1d")
        # ターゲット銘柄
        n = 22  # 最高値・最安値の期間
        atr_period = 22  # ATRの計算期間
        multiplier = 3  # ATRの倍率

        # 計算結果をデータフレームに追加
        data["EMA_200"] = calculate_ema(data["Open"], 200)
        data = calculate_ce(data,max_min_period=n, atr_period=atr_period, multiplier=multiplier )

        # data.to_csv("nyan.csv")
        data_last = data.iloc[[-1]].copy()  # Use [[-1]] to keep it as a DataFrame
        if gap(data_last["Chandelier_Long"].values[0], data_last["Open"].values[0]) > 0.07 or \
        gap(data_last["Chandelier_Short"].values[0], data_last["Open"].values[0]) > 0.07:
            # If either gap is greater than 5%, add action to the list
            if data_last["Open"].values[0] < data_last["Chandelier_Long"].values[0] and data_last["Open"].values[0] < data_last["Chandelier_Short"].values[0]:
                data_last["action"] = "long"
                save_list.append({"ticker": ticker, "action": "long"})
            elif data_last["Open"].values[0] > data_last["Chandelier_Long"].values[0] and data_last["Open"].values[0] > data_last["Chandelier_Short"].values[0]:
                data_last["action"] = "short"
                save_list.append({"ticker": ticker, "action": "short"})
    
    finally:
        continue

    # # グラフ描画
    # plt.figure(figsize=(12, 6))
    # plt.rcParams['font.family'] = 'MS Gothic'
    # plt.plot(data.index, data["Close"], label="Close Price", color="black")
    # plt.plot(data.index, data["EMA_200"], label="EMA 200", linestyle="dashed")
    # plt.plot(data.index, data["Chandelier_Long"], label="Chandelier Exit Long", linestyle="dashed", color="blue")
    # plt.plot(data.index, data["Chandelier_Short"], label="Chandelier Exit Short", linestyle="dashed", color="red")
    # plt.legend()
    # plt.title(f"{ticker} - {name} Exit Strategy")
    # plt.xlabel("Date")
    # plt.ylabel("Price")
    # plt.grid()
    # plt.show()

save_list = pd.DataFrame(save_list)
save_list.to_csv("result_screen.csv", index=False)