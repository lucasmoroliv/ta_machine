import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt
import goodtimer2,digger2,asimov1,classification2

def main():
    df_file,object_file,timeframe,start_candle,end_candle,buy_candle,buy_time,sell_candle,sell_time,min_profit = researcher_parameters()
    goodtimer,digger,asimov,classification = module_version()
    goodtimes = goodtimer.callable(object_file,timeframe)
    candles0_array = digger.callable(goodtimes,df_file)

    info_list = asimov.callable(df_file,candles0_array,start_candle,end_candle)
    dict_arrays = arraify(info_list)

    profit_array = get_profit_array(dict_arrays,buy_candle,buy_time,end_candle)

# -----------------------------------------------------------------------------------
    info_as_feature = ['rsi']
    lables_list = ['candle_4_high']
    score = classification.callable(dict_arrays,info_as_feature,lables_list,min_profit)
    print(score)

def classification_parameters():
    features_array = make_features()
    labels_array = make_labels()
def make_features():

# -----------------------------------------------------------------------------------
# Probably will be better to set up the features and labels array here at researcher1 and through
# data to classification already done to train the classifier. Or at least done to split the arrays in
# training and test data.


def researcher_parameters():
    df_file = '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
    object_file = '../warehouse/trendlines/' + '30min_2017-05-01_2018-04-19_40_100_4_9_0015_001_8.txt'
    timeframe = ['2014-01-04 00:00:00','2018-04-19 00:00:00']
    start_candle = -3
    end_candle = 6
    buy_candle = 1
    buy_time = 'open'
    sell_candle = 4
    sell_time = 'high'
    min_profit = 0.01
    return df_file,object_file,timeframe,start_candle,end_candle,buy_candle,buy_time,sell_candle,sell_time,min_profit

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
    goodtimer = goodtimer2
    digger = digger2
    asimov = asimov1
    classification = classification2
    return goodtimer,digger,asimov,classification

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
