import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys
sys.path.append('../builders')
from pprint import pprint
import momentum_indicators
import matplotlib.pyplot as plt

def main():
    object_file = '../warehouse/trendlines/' + '30min_2017-05-01_2018-04-19_40_100_4_9_0015_001_8.txt'
    df_file = '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
    timeframe = ['2017-05-10 00:00:00','2018-04-20 00:00:00']
    goodtimes = goodtimer2.callable(object_file,timeframe)
    candles0_array = digger2.callable(goodtimes,df_file)
    info_list = callable(candles0_array,df_file)
    pprint(info_list)

def callable(df_file,candles0_array,start_candle,end_candle):
    info_list = get_info_list(df_file,candles0_array,start_candle,end_candle)
    return info_list

def get_info_list(df_file,candles0_array,start_candle,end_candle):
    df_old = get_dataframe(df_file)
    df = df_old.set_index('timestamp')
    rsi = momentum_indicators.rsi(df_file)
    df = update_df(df,'rsi',rsi[:,1])
    candle_sec = df_old['timestamp'][1] - df_old['timestamp'][0]
    candles_list = []
    for row in candles0_array:
        candles = {}
        ts_candle0 = row
        for index in range(start_candle,end_candle+1):
            ts = ts_candle0 + candle_sec*index
            candles[index] = {
                # 'ts': ts,
                'open': df['open'][ts],
                'high': df['high'][ts],
                'low': df['low'][ts],
                'rsi': df['rsi'][ts],
            }
        candles_list.append(candles)
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
