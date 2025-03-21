
# %%
from IPython import get_ipython
import numpy as np
import pandas as pd
import math
import itertools

from matplotlib import rc
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from pylab import rcParams
from pandas_datareader import data
from scipy import signal

import os
import datetime as dt
import seaborn as sns


# %%
# PLOTTING SETUP
# get_ipython().run_line_magic('matplotlib', 'inline')
# get_ipython().run_line_magic('config', "InlineBackend.figure_format='retina'")
# register_matplotlib_converters()
# sns.set(style='whitegrid', palette='muted', font_scale=1.5)
# rcParams['figure.figsize'] = 22, 10

# %%
# COMMODITY
dateTimeObj = dt.datetime.now()
today = dateTimeObj.strftime("%Y-%m-%d")

symbol = "BTC-USD"
date = today
# filename = '/data/%s/Yahoo_BTCUSD_d.csv.ta.csv' % symbol

# %%

# **************************************************************************
# download from yahoo the daily charts
# **************************************************************************
def download(symbol, date, days=365):
    
    if date is None:    
        dateTimeObj = dt.datetime.now()
    else:
        dateTimeObj = dt.datetime.strptime(date, "%Y-%m-%d")

    date = dateTimeObj.strftime("%Y-%m-%d")
    date_start = (dateTimeObj - dt.timedelta(days=days)).strftime("%Y-%m-%d")

    # dt = datetime.today() - timedelta(days=days_to_subtract)
    #  date_time_obj = datetime. strptime(date_time_str, '%d/%m/%y %H:%M:%S')
    df_source = data.DataReader(symbol, 
                start=date_start, 
                end=date, 
                data_source='yahoo')
    df_source['Date'] = df_source.index
    df_source = df_source.drop(columns=['Adj close'])
    return df_source

# %%
def minmaxTwoMeasures(df, measureMin, measureMax, column, order=2):
    # import numpy as np
    # https://stackoverflow.com/questions/31070563/find-all-local-maxima-and-minima-when-x-and-y-values-are-given-as-numpy-arrays
    
    # import matplotlib.pyplot as plt

    # x = np.array(df["Date"].values)
    df.loc[:, 'DateTmp'] = df.index
    x = np.array(df["DateTmp"].values)
    y1 = np.array(df["low"].values)
    y2 = np.array(df["high"].values)

    # sort the data in x and rearrange y accordingly
    sortId = np.argsort(x)
    x = x[sortId]
    y1 = y1[sortId]
    y2 = y2[sortId]

    df.loc[:, column] = 0

    # this way the x-axis corresponds to the index of x
    maxm = signal.argrelextrema(y2, np.greater, order=order)  # (array([1, 3, 6]),)
    minm = signal.argrelextrema(y1, np.less, order=order)  # (array([2, 5, 7]),)
    for elem in maxm[0]:
        # max 
        df.iloc[elem, df.columns.get_loc(column)] = 1 
    for elem in minm[0]:
        # min
        df.iloc[elem, df.columns.get_loc(column)] = -1
    return  df.drop(columns=['DateTmp'])


def isMin(df,i):
    return df["FlowMinMax"].iat[i] == -1

def isMax(df,i):
    return df["FlowMinMax"].iat[i] == 1

# def hash(wave):
#     s = ""

#     for digit in wave:
#         s += str(digit) + "."
#     return s

def distance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist  


def isElliottWave(df, value, i0, i1, i2, i3, i4, i5, ia, ib, ic):
    values = df[value].to_numpy()  # Convert to NumPy array for faster access

    # Ensure all key points are valid minima or maxima
    if not (isMin(df, i0) and isMin(df, i2) and isMin(df, i4) and isMin(df, ia) and isMin(df, ic)):
        return None
    if not (isMax(df, i1) and isMax(df, i3) and isMax(df, i5) and isMax(df, ib)):
        return None

    # Check wave structure conditions
    if not (values[i5] > max(values[i1], values[i2], values[i3], values[i4])):
        return None
    if not (values[i1] > values[i0] > values[i2] > values[i4] and values[i3] > values[i2]):
        return None
    if not (values[i4] > values[i1] and values[i5] > values[i3] > values[i4]):
        return None

    # Length calculations (wave lengths must follow Elliott Wave rules)
    w1Len = distance(i0, values[i0], i1, values[i1])
    w3Len = distance(i2, values[i2], i3, values[i3])
    w5Len = distance(i4, values[i4], i5, values[i5])

    if not (w3Len >= w1Len and w3Len >= w5Len):  # Wave 3 should be longest
        return None

    # Uptrend confirmation
    if not (values[i5] > max(values[ia], values[ib], values[ic]) and values[ib] > values[ia] > values[ic]):
        return None

    return [i0, i1, i2, i3, i4, i5, ia, ib, ic]


# def isElliottWave(df,value,i0,i1,i2,i3,i4,i5,ia,ib,ic):
#     result = None
#     # print(".")

#     if not isMin(df,i0) or not isMin(df,i2) or not isMin(df,i4) or not isMin(df,ia) or not isMin(df,ic):
#         return result

#     if not isMax(df,i1) or not isMax(df,i3) or not isMax(df,i5) or not isMax(df,ib):
#         return result

#     isi5TheTop = df[value].iat[i5] > df[value].iat[i1] and df[value].iat[i5] > df[value].iat[i2] and df[value].iat[i5] > df[value].iat[i3] and df[value].iat[i5] > df[value].iat[i4]  
#     if not isi5TheTop:
#         return result

#     if not df[value].iat[i1] > df[value].iat[i0]:
#         return result

#     if not df[value].iat[i1] > df[value].iat[i2]:
#         return result
    
#     if not df[value].iat[i2] > df[value].iat[i0]:
#         return result
       
#     if not df[value].iat[i3] > df[value].iat[i2]:
#         return result

#     # w1Len = np.abs(df[value].iat[i1]-df[value].iat[i0])
#     # w2Len = np.abs(df[value].iat[i1]-df[value].iat[i2])
#     w1Len = distance(i0,df[value].iat[i0],i1,df[value].iat[i1])
#     # w2Len = calculateDistance(i1,df[value].iat[i1],i2,df[value].iat[i2])
#     # if not w2Len < 2*w1Len:
#     #     return result

#     if not df[value].iat[i2] > df[value].iat[i0]:
#         return result

#     # result = [i0,i1,i2,i3]

#     if not df[value].iat[i3] > df[value].iat[i4]:
#         return result

#     if not df[value].iat[i4] > df[value].iat[i2]:
#         return result

#     # w3Len = np.abs(df[value].iat[i3]-df[value].iat[i2])
#     w3Len = distance(i2,df[value].iat[i2],i3,df[value].iat[i3])
#     # w4Len = np.abs(df[value].iat[i4]-df[value].iat[i3])

#     if not df[value].iat[i4] > df[value].iat[i1]:
#         return result

#     # result = [i0,i1,i2,i3,i4]

#     if not df[value].iat[i5] > df[value].iat[i4]:
#         return result

#     if not df[value].iat[i5] > df[value].iat[i3]:
#         return result

#     # w5Len = np.abs(df[value].iat[i5]-df[value].iat[i4])
#     w5Len = distance(i4,df[value].iat[i4],i5,df[value].iat[i5])

#     if (w3Len < w1Len and w3Len < w5Len):
#         return result

#     # uptrend
#     result = [i0,i1,i2,i3,i4,i5]

#     isi5TheTop = df[value].iat[i5] > df[value].iat[ia]  and df[value].iat[i5] > df[value].iat[ib]  and df[value].iat[i5] > df[value].iat[ic]
#     if not isi5TheTop:
#         return result

#     if not df[value].iat[i5] > df[value].iat[ia]:
#         return result
    
#     # waLen = calculateDistance(i5,df[value].iat[i5],ia,df[value].iat[ia])
#     # wcLen = calculateDistance(ib,df[value].iat[ib],ic,df[value].iat[ic])

#     # if waLen > wcLen:
#     #     return result

#     # if not (df[value].iat[i3] >= df[value].iat[ia] and df[value].iat[ia] >= df[value].iat[i4]):
#     #     return result

#     if not df[value].iat[i5] > df[value].iat[ib]:
#         return result

#     if not df[value].iat[ib] > df[value].iat[ia]:
#         return result

#     if not df[value].iat[ia] > df[value].iat[ic]:
#         return result

#     if not df[value].iat[ib] > df[value].iat[ic]:
#         return result

#     # if not df[value].iat[ia] > df[value].iat[ic]:
#     #     return result

#     # uptrend and retracement
#     result = [i0,i1,i2,i3,i4,i5,ia,ib,ic]

#     return result 


def ElliottWaveDiscovery(df, measure):
    values = df[measure].to_numpy()  # Convert to NumPy for fast indexing

    # Precompute all local minima and maxima
    min_indices = [i for i in range(len(values)) if isMin(df, i)]
    max_indices = [i for i in range(len(values)) if isMax(df, i)]

    waves = []

    for i0, i1, i2, i3, i4, i5 in itertools.combinations(min_indices + max_indices, 6):
        print(i0,i1,i2,i3,i4,i5)
        if i0 >= i1 or i1 >= i2 or i2 >= i3 or i3 >= i4 or i4 >= i5:
            continue  # Ensure the correct order

        # Check if i5 is the highest peak
        if values[i5] > max(values[i1], values[i2], values[i3], values[i4]):
            for ia, ib, ic in itertools.combinations(min_indices + max_indices, 3):
                if i5 >= ia or ia >= ib or ib >= ic:
                    continue

                wave = isElliottWave(df, measure, i0, i1, i2, i3, i4, i5, ia, ib, ic)
                if wave and wave not in waves:
                    waves.append(wave)
                    print(wave)

    return waves

# def ElliottWaveDiscovery(df, measure):

#     def minRange(df, start, end):
#         def localFilter(i):
#             return isMin(df,i)
#         return filter(localFilter, list(range(start,end)))

#     def maxRange(df, start, end):
#         def localFilter(i):
#             return isMax(df,i)
#         return filter(localFilter, list(range(start,end)))


#     waves = []
#     for i0 in minRange(df,0,len(df)):
#         print(i0)
#         for i1 in maxRange(df,i0+1,len(df)):
#             print(i1)
#             for i2 in minRange(df,i1+1,len(df)):
#                 print(i2)
#                 for i3 in maxRange(df,i2+1,len(df)):
#                     print(i3)
#                     for i4 in minRange(df,i3+1,len(df)):
#                         print(i4)
#                         for i5 in maxRange(df,i4+1,len(df)):
#                             print(i5)

#                             isi5TheTop = df[measure].iat[i5] > df[measure].iat[i1] and df[measure].iat[i5] > df[measure].iat[i2] and df[measure].iat[i5] > df[measure].iat[i3] and df[measure].iat[i5] > df[measure].iat[i4]  
#                             if isi5TheTop:

#                                 for ia in minRange(df,i5+1,len(df)):
#                                     for ib in maxRange(df,ia+1,len(df)):
#                                         for ic in minRange(df,ib+1,len(df)):
#                                             wave = isElliottWave(df,measure, i0,i1,i2,i3,i4,i5,ia,ib,ic)
#                                             if wave is None:
#                                                 continue
#                                             if not wave in waves:
#                                                 waves.append(wave)
#                                                 print(wave)

#     return waves

# %%

def draw_wave(df,df_waves,w):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(df['close'],       label='close', color="blue", linestyle="-", alpha=0.5)
    ax.plot(df_waves['close'], label='close', color="black", linestyle="-", alpha = 0.5)

    ax.plot(df_waves['close'], 'ko', markevery=None)

    df_waves.loc[:, "wave"] = None
    for i in range(0,len(w)):
            df_waves['wave'].iat[w[i]] = df_waves['close'].iat[w[i]]

    df_filtered_waves = df_waves.loc[pd.notnull(df_waves.wave)]
    ax.plot(df_filtered_waves['wave'], color="red", linewidth=3.0)
    plt.show()   

# %%

# select the waves the best fit the chart
def filterWaveSet(waves, min_len=6, max_len=6, extremes=True):

    result = []
    for w in waves:
        l = len(w)
        if min_len <= l and l <= max_len:
            result.append(w)
    
    if not extremes:
        return result

    # find the max
    max = 0 
    for w in result:
        if w[len(w)-1] >= max:
            max = w[len(w)-1]
        
    #  filter the max
    result2 = []
    for w in result:
        if w[len(w)-1] == max:
            result2.append(w)

    # find the min
    min = max
    for w in result2:
        if w[0] <= min:
            min = w[0]    

    #  filter the min
    result = []
    for w in result2:
        if w[0] == min:
            result.append(w)

    return result


# %%
import math

# given one line defined with two points
def line(wa,wb, x):
    x1 = wa[0]
    y1 = wa[1]
    x2 = wb[0]
    y2 = wb[1]
    y = ((y2-y1)/(x2-x1))*(x-x1) + y1
    return y


def elliottWaveLinearRegressionError(df_waves, w, value):
    diffquad = 0
    for i in range(1,len(w)):
        wa = [ w[i-1], df_waves[value].iat[w[i-1]] ]
        wb = [ w[i  ], df_waves[value].iat[w[i  ]] ]
        # for each line, we calculate the average squared error
        
        for xindex in range(wa[0],wb[0]):
            yindex = df_waves[value].iat[xindex]
            yline = line(wa,wb, xindex)

            diffquad += (yindex-yline) ** 2

    return math.sqrt(diffquad)/(w[len(w)-1]-w[0])

def findBestFitWave(df,value,waves):

    avg = np.Inf
    # avg = 0
    df_waves = df[[value,"FlowMinMax"]]
    result = []
    for w in waves:
        # for each wave, we generate the lines
        tmp = elliottWaveLinearRegressionError(df_waves, w, value)

        if tmp < avg:
            # print(averages)
            print(w,tmp)
            avg = tmp
            result = w
    return result


# %%

def buildWaveChainSet(waves, startwith=9):

    def addList(list, wavelist):
        k = 0
        for w in wavelist:
            k += len(w)
        key = str(k)
        if not key in list:
            list[key] = []
        list[key].append(wavelist)
        print(wavelist)
        return list


    print("chainsets")
    list = {}
    for w1 in [wave for wave in waves if len(wave) == startwith]:
        wavelist = [w1]
        if len(w1) == 9:
            for w2 in waves:
                if (len(w2) <= len(w1)):
                    if w1[len(w1)-1] == w2[0]:
                        wavelist.append(w2)
                        addList(list, wavelist.copy())
                        wavelist.pop(-1)
        else:
            # if w1 is not complete, i can't attach another wave
            addList(list, wavelist)
    return list           


# %%
# find the best sequence

            
def findBestFitWaveChain(df_waves, waveChainDict):

    bestFit = {}

    for key in waveChainDict:
        waveChainSet = waveChainDict[key]

        polylines = []
        for chain in waveChainSet:
            #  transform the chain in a polyline
            poly = []
            for wave in chain:
                for w in wave:
                    if not w in poly:
                        poly.append(w)
            polylines.append(poly)

        # select the polyline with wider coverage
        
        # polylines = filterWaveSet(polylines, min_len=9, max_len=99, extremes=False)
        bestFit[key] = findBestFitWave(df_waves, polylines)
    
    return bestFit



# %%
# -------------------------------------------------
#  given a timeline, we generate all the possible waves
# -------------------------------------------------


# %%
def ElliottWaveFindPattern(df_source, measure, granularity, dateStart, dateEnd, extremes=True):

    #  subset to consider
    mask = (dateStart <= df_source.Date) & (df_source.Date <= dateEnd)
    df = df_source.loc[mask]
    df.set_index("Date")

    #  find min and max
    FlowMinMax = minmaxTwoMeasures(df,"close","close","FlowMinMax",granularity)

    df = FlowMinMax
    df_samples = df.loc[df['FlowMinMax'] != 0]

    draw_wave(df, df_samples, [])

    print("start ", len(FlowMinMax))
    waves =  ElliottWaveDiscovery(df_samples[[measure,"FlowMinMax"]], measure)
    print("waves")
    print(waves)
    filtered_waves = filterWaveSet(waves, 5, 9, extremes=extremes)
    print("selected waves")
    print(filtered_waves)
    # split waves in sets based on their length
    waves_for_len = {}
    for w in filtered_waves:
        if not str(len(w)) in waves_for_len[len(w)]:
            waves_for_len[len(w)] = []
        waves_for_len[len(w)].append(w)

    # select the best fit
    for k in waves_for_len.keys:
        result = findBestFitWave(df_samples, measure, waves_for_len[k])
        print("best fit")
        print(result)
        draw_wave(df, df_samples, result)

    # df_waves = df[[value,"FlowMinMax"]]
    chainSet = buildWaveChainSet(filtered_waves)
    # bestChain = findBestFitWaveChain(df_waves, chainSet)
    print("chainset best fit",len(chainSet))
    # print(bestChain)
    # draw_wave(df, df_samples, bestChain)