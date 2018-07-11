import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import digger2

import matplotlib.pyplot as plt

def callable(p,candles0_array):
    info_list = get_info_list(p,candles0_array,p['buy'])
    return info_list

def get_info_list(p,candles0_array,buy):
    df = get_dataframe(p['path_candle_file'])
    td_s_array = td_array(p['path_td_file'],df)
    candle_sec = df['timestamp'][1] - df['timestamp'][0]
    df = df.set_index('timestamp')
    df = update_df(df,'td',td_s_array[:,1])
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

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
