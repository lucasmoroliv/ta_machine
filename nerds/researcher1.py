import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt
import tourist1,digger1,sculptor1,sorcerer1

def main():
# Below we assign the main variables of the program with the help of a function.
    path_df_file,path_object_file,timeframe,start_candle,end_candle,buy_candle,buy_time,sell_candle,sell_time,min_profit = researcher_parameters()
# Using a second function, we choose the versions of the modules we have in order to make
# our analysis.
    tourist,digger,sculptor,sorcerer = module_version()
# The goodtimes is a two column array. Each line of it has the inferior and
# superior limits of the intervals found by our expert tourist.
    goodtimes = tourist.callable(path_df_file,path_object_file,timeframe)
# Next we get a one column array that has the timestamp of each candle0, which
# are candles digger found with probably some interesting pattern.
    candles0_array = digger.callable(goodtimes,path_df_file)
# The sculptor gives us is a list of dictionaries that have information we choose
# (like ohlc, etc), of the candles we choose related to candle0, of each single
# candle0 found by digger.
    info_list = sculptor.callable(path_df_file,candles0_array,start_candle,end_candle)
# The function gets the data given by info_list and change it so it gets a format
# more suitable for further processing.
    dict_arrays = arraify(info_list)
# -----------------------------------------------------------------------------------



    profit_array = get_profit_array(dict_arrays,buy_candle,buy_time,end_candle)
    pprint(info_list)

# -----------------------------------------------------------------------------------
#     info_as_feature = ['rsi']
#     lables_list = ['candle_4_high']
#     score = sorcerer.callable(dict_arrays,info_as_feature,lables_list,min_profit)
#     print(score)
# -----------------------------------------------------------------------------------

def researcher_parameters():
    path_df_file = '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
    path_object_file = '../warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt'
    timeframe = ['2014-01-04 00:00:00','2018-04-19 00:00:00']
    start_candle = -3
    end_candle = 6
    buy_candle = 1
    buy_time = 'open'
    sell_candle = 4
    sell_time = 'high'
    min_profit = 0.01
    return path_df_file,path_object_file,timeframe,start_candle,end_candle,buy_candle,buy_time,sell_candle,sell_time,min_profit

def get_profit_array(dict_arrays,buy_candle,buy_time,end_candle):
    dict_profits = {}
    price_buy = dict_arrays['candle_{0}_{1}'.format(buy_candle,buy_time)]
    print(type(price_buy))
    for candle in range(buy_candle+1,end_candle+1):
        dict_profits['o{0}_h{1}'.format(buy_candle,candle)] = ( dict_arrays['candle_{0}_{1}'.format(candle,'high')] - price_buy ) / price_buy
    return dict_profits

def general_stats(buy_candle,buy_time):
    pass

def module_version():
    tourist = tourist1
    digger = digger1
    sculptor = sculptor1
    sorcerer = sorcerer1
    return tourist,digger,sculptor,sorcerer

def arraify(info_list):
    dict_lists = {}
    for candle in info_list[0]:
        for info in info_list[0][candle]:
            dict_lists['candle_{0}_{1}'.format(candle,info)] = []
    for graph in info_list:
        for candle in graph:
            for info in graph[candle]:
                dict_lists['candle_{0}_{1}'.format(candle,info)].append(graph[candle][info])
    dict_arrays = {}
    for key in list(dict_lists):
        dict_arrays[key] = np.array(dict_lists[key])
    return dict_arrays

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
