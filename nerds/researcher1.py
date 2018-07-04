import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt
# By importing the module "parameters" we define the main variables of the
# program and add them to the module's scope.
from parameters import *

def main():
# This first block of code does a lot of stuff. It initially defines a handfull
# of parameters that will constrain our analysis. Next, we choose the version of
# the nerds that we will use using module_version function. At last, we change
# the structure of the data processed through the nerds with the arraify so it
# becomes suitable for the analysis we will made further on.
# -----------------------------------------------------------------------------------
# Using this following function, we choose the versions of the modules we have
# in order to make our analysis.
    tourist,digger,sculptor,sorcerer = module_version()
# The goodtimes is a two column array. Each line of it has the inferior and
# superior limits of the intervals found by our expert tourist.
    goodtimes = tourist.callable(path_candle_file,path_trendline_file ,timeframe)
# Next we get a one column array that has the timestamp of each candle0, which
# are candles digger found with probably some interesting pattern.
    candles0_array = digger.callable(goodtimes,path_candle_file)
# The sculptor gives us is a list of dictionaries that have information we
# choose (like ohlc, etc), of the candles we choose related to candle0, of each
# single candle0 found by digger.
    info_list = sculptor.callable(path_candle_file,candles0_array,start_candle,end_candle)
# The function gets the data given by info_list and change it so it gets a
# format more suitable for further processing.
    dict_arrays = arraify(info_list)
# -----------------------------------------------------------------------------------

# Below we find the analysis code block.
# -----------------------------------------------------------------------------------
    profit_array = get_profit_array(dict_arrays)
    keys_list = list(profit_array.keys())
    sample_amt = profit_array[keys_list[0]].shape[0]
    for key in keys_list:
        success_amt = profit_array[key][profit_array[key]>0.007].shape[0]
# "ros" stands for "rate_of_success"
        ros = success_amt/sample_amt
        print(ros)




# -----------------------------------------------------------------------------------

def get_profit_array(dict_arrays):
    dict_profits = {}
    price_buy = dict_arrays['candle_{0}_{1}'.format(buy['candle'],buy['moment'])]
    for candle in range(buy['candle']+1,end_candle+1):
        dict_profits['o{0}_h{1}'.format(buy['candle'],candle)] = ( dict_arrays['candle_{0}_{1}'.format(candle,'high')] - price_buy ) / price_buy
    return dict_profits

def module_version():
    import tourist1,digger1,sculptor1,sorcerer1
    return tourist1,digger1,sculptor1,sorcerer1

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
