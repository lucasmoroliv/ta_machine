import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys
sys.path.append('../builders')
from pprint import pprint
import momentum_indicators
import matplotlib.pyplot as plt

def callable(p,candles0_array):
    info_list = get_info_list(p,candles0_array)
    return info_list

def get_info_list(p,candles0_array):
    df_old = get_dataframe(p['path_candle_file'])
    df = df_old.set_index('timestamp')
    rsi = momentum_indicators.rsi(p['path_candle_file'])
    df = update_df(df,'rsi',rsi[:,1])
    candle_sec = df_old['timestamp'][1] - df_old['timestamp'][0]
    candles_list = []
    for row in candles0_array:
        candles = {}
        ts_candle0 = row
        ts_buy = ts_candle0 + candle_sec*1
        for index in range(p['buy']['candle'],p['sell']['candle']+1):
            ts = ts_candle0 + candle_sec*index
            candles[index] = {
                'frombuytothishigh': ( df['high'][ts] - df['open'][ts_buy] ) / df['open'][ts_buy],
                'frombuytothislow': ( df['low'][ts] - df['open'][ts_buy] ) / df['open'][ts_buy],
            }
        candles_list.append(candles)
    p['sculptor']['keys'] = list(candles_list[0][list(candles_list[0])[0]].keys())
    return candles_list



def update_df(df,name,array):
    serie = pd.Series(array)
    df[name] = array
    return df

def get_dataframe(file):
    return pd.read_csv(file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])


if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
