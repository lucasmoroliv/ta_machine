import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys
from pprint import pprint
sys.path.append('../builders')
import momentum_indicators
import matplotlib.pyplot as plt
import tourist1

def callable(p,goodtimes):
# The callable function receives the goodtimes arary and df_file from the
# researcher module, and returns to it an one column array containing the
# timestamp of every candle0 found by digger. The pattern function will define
# the criteria for finding the candles 0. We can call any pattern function
# declared in this module.
    candles0_array = pattern1(p,30,goodtimes)
    return candles0_array

def pattern1(p,limit,goodtimes):
    rsi = momentum_indicators.rsi(p['path_candle_file'])
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
