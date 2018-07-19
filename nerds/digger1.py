import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys
from pprint import pprint
sys.path.append('../builders')
import momentum_indicators
import matplotlib.pyplot as plt
import tourist1

def main():
    p = {
    'path_candle_file' : '../builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'path_trendline_file': '../builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
    'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
    'buy' : {'candle':'1','moment':'5'},
    'sell' : {'candle':'4-6','moment':'11c'},
    'tourist': {
        'version': 'tourist1',
        'mode': 'greater_than_limit',
        'condition_parameter': 'm',
        'limit': 0,
        'limit1': 0,
        'limit2': 0
    },
    'digger': {'version': 'digger1'},
    'sculptor': {'version': 'sculptor3'},
    'researcher': {'version': 'researcher1'}
    }

    goodtimes = tourist1.callable(p)

    units_list = callable(p,goodtimes)
    # units_list = callable(p)
    pprint(units_list)
    
def callable(p,goodtimes=None):

    threshold = 30
    p['digger']['rsi_threshold'] = threshold
    units_list = pattern1(p,threshold,goodtimes)
    return units_list

def pattern1(p,limit,goodtimes):
    rsi = momentum_indicators.rsi(p['path_candle_file'])
    units_list = []
    if isinstance(goodtimes, np.ndarray):
        for index in range(goodtimes.shape[0]):
            ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
            mini_rsi = filter_rsi(rsi,ts_timeframe)
            for i in range(mini_rsi.shape[0])[:-1]:
                if mini_rsi[i,1] < limit and mini_rsi[i-1,1] > limit:
                    units_list.append({'0': {'ts': mini_rsi[i,0]}})
    else:       
        ts_timeframe = [calendar.timegm(time.strptime(p['timeframe'][0], '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe'][1], '%Y-%m-%d %H:%M:%S'))]
        mini_rsi = filter_rsi(rsi,ts_timeframe) 
        for i in range(mini_rsi.shape[0])[:-1]:
            if mini_rsi[i,1] < limit and mini_rsi[i-1,1] > limit:
                units_list.append({'0': {'ts': mini_rsi[i,0]}})
    return units_list
    
def filter_rsi(rsi,timeframe):
    return rsi[(rsi[:,0] >= timeframe[0]) & (rsi[:,0] <= timeframe[1])]

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)







