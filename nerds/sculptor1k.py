import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import digger1k

import matplotlib.pyplot as plt

# def main():
#     object_file = 'td_setup_30min_bitstamp.csv'
#     df_file = '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
#     timeframe = ['2017-05-10 00:00:00','2018-04-20 00:00:00']
#     # df_td = generate_df_td.callable()
#     df = get_dataframe(df_file)
#     td_s_array = td_array(object_file,df)
#     # candles0_array = goodtimertd.callable(object_file,timeframe)
#     # callable(object_file,timeframe,df)
#     info_list = callable(object_file, timeframe, df, td_s_array)
#     pprint(info_list)

def callable(p,candles0_array):
    info_list = get_info_list(p,candles0_array,p['buy'])
    return info_list

def get_dataframe(file):
    return pd.read_csv(file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])

def td_array(td_file,df):
    list1 = []
    list2 = []
    count = 0
    # df2 = pd.DataFrame()
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
                'open': df['open'][ts],#-open_buy_candle)/open_buy_candle,
                'high': df['high'][ts],#-open_buy_candle)/open_buy_candle,
                'low': df['low'][ts],#-open_buy_candle)/open_buy_candle,
                'close': df['close'][ts],#-open_buy_candle)/open_buy_candle,
                'volume': df['volume'][ts],#-volume_buy_candle)/volume_buy_candle,
                'amplitude': df['amplitude'][ts],#-amplitude_buy_candle)/amplitude_buy_candle,
                'change': df['change'][ts],
                'td_s': df['td'][ts],
            }
        candles_list.append(candles)
    return candles_list


#
# def pattern1(big_array):
#     small_array = big_array[big_array[:,1]==9]
#     small_array = small_array[:,0]
#     return small_array
#
# def get_data(object_file,timeframe):
#     with open(object_file, newline='') as csvfile:
#         data = csv.reader(csvfile, delimiter=' ', quotechar='|')
#         list = []
#         big_list = []
#         for row in data:
#             ts_start = int(row[0].split(',')[0])
#             td = int(row[0].split(',')[1])
#             big_list.append([ts_start,td])
#         big_array = np.array(big_list)
#     return big_array


if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
