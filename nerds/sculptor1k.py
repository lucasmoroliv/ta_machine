import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import digger1k

import matplotlib.pyplot as plt

def callable(p,candles0_array):
    info_list = get_info_list(p,candles0_array,p['buy'])
    return info_list

def get_dataframe(file):
    return pd.read_csv(file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])

def td_array(td_file,df):
    list1 = []
    list2 = []
    count = 0
    td_s_array = np.zeros([df.shape[0],2])
    with open(td_file, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in data:
            td_s_array[count,0] = int(row[0].split(',')[0])
            td_s_array[count,1] = int(row[0].split(',')[1])
            count += 1
    return td_s_array

def update_df(df,name,array):
    serie = pd.Series(array)
    df[name] = array
    return df

def get_info_list(p,candles0_array,buy):
    df = get_dataframe(p['path_candle_file'])
    td_s_array = td_array(p['path_td_file'],df)
    candle_sec = df['timestamp'][1] - df['timestamp'][0]
    candles_list = []
    df = df.set_index('timestamp')
    df = update_df(df,'td',td_s_array[:,1])
    for row in candles0_array:
        candles = {}
        ts_candle0 = row
        ts_buy_candle = ts_candle0 + candle_sec*buy['candle']
        open_buy_candle = df['open'][ts_buy_candle]
        volume_buy_candle = df['volume'][ts_buy_candle]
        amplitude_buy_candle = df['amplitude'][ts_buy_candle]
        for index in range(p['end_candle']+1):
            ts = ts_candle0 + candle_sec*index
            candles[index] = {
                'ts' : ts,
                'open': df['open'][ts],
                'high': df['high'][ts],
                'low': df['low'][ts],
                'close': df['close'][ts],
                'volume': df['volume'][ts],
                'amplitude': df['amplitude'][ts],
                'change': df['change'][ts],
                'td_s': df['td'][ts],
            }
        candles_list.append(candles)
    return candles_list

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
