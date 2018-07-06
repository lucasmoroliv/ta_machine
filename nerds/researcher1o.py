import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt

def callable(p,info_list):
    dict_arrays = arraify(info_list)
    # x = success_low_stats(p,dict_arrays)
    x = get_success_rate(p,dict_arrays)
    return x
    # profit_array = get_profit_array(dict_arrays,p['buy'],p['end_candle'])
    # keys_list = list(profit_array.keys())
    # sample_amt = profit_array[keys_list[0]].shape[0]
    # for key in keys_list:
    #     success_amt = profit_array[key][profit_array[key]>p['target']].shape[0]
    #     ros = success_amt/sample_amt
    # return ros


def success_low_stats(p,dict_arrays):
    profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
    success_array = [profit_array>p['target']]
    return success_rate

def get_success_array(p,dict_arrays):
    profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
    success_array = profit_array[profit_array>p['target']]
    return success_array

def get_success_rate(p,dict_arrays):
    profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
    success_amt = profit_array[profit_array>p['target']].shape[0]
    sample_amt = profit_array.shape[0]
    success_rate = success_amt/sample_amt
    return success_rate

def get_profit_array(dict_arrays,buy,end_candle):
    dict_profits = {}
    price_buy = dict_arrays['candle_{0}_{1}'.format(buy['candle'],buy['moment'])]
    for candle in range(buy['candle']+1,end_candle+1):
        dict_profits['o{0}_h{1}'.format(buy['candle'],candle)] = ( dict_arrays['candle_{0}_{1}'.format(candle,'high')] - price_buy ) / price_buy
    return dict_profits

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
