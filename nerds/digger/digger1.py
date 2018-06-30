import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import momentum_indicators,trendline5
import matplotlib.pyplot as plt
import goodtimer2

def main():
    object_file = '../warehouse/trendlines/' + '30min_2017-05-01_2018-04-19_40_100_4_9_0015_001_8.txt'
    df_file = '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
    timeframe = ['2017-05-10 00:00:00','2018-04-20 00:00:00']
    goodtimes = goodtimer2.callable(object_file,timeframe)
    canldles0_array = callable(goodtimes,df_file)
    pprint(canldles0_array)

def callable(goodtimes,df_file):
    candles0_array = pattern1(30,goodtimes,df_file)
    return candles0_array

def pattern1(limit,goodtimes,df_file):
# The function returns a list with the timestamps where we see this pattern happening.
# First we get the rsi.
    rsi = momentum_indicators.rsi(df_file)
    sample = []
    for index in range(goodtimes.shape[0]):
        ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
        mini_rsi = filter_rsi(rsi,ts_timeframe)
        for i in range(mini_rsi.shape[0])[:-1]:
            if mini_rsi[i,1] < limit and mini_rsi[i-1,1] > limit:
                sample.append(mini_rsi[i,0])
    return sample

def filter_rsi(rsi,timeframe):
    return rsi[(rsi[:,0] >= timeframe[0]) & (rsi[:,0] <= timeframe[1])]

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
