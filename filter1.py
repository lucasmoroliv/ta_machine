# Input: p
# Outuput: List of [<start>,<end>] objects, where <start> and <end> are the inferior and 
# superior limits of each filtered period. The program find the periods inside p['timeframe']
# where certain conditions are met. 
# The conditions used in this program to do this filtering are related to SMA and EMA lines.

import time,datetime,calendar
from pprint import pprint
from builders import momentum_indicators
import numpy as np
import pandas as pd

def main():
    p = {
    'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'timeframe_start' : '2014-01-01 00:00:00',
    'timeframe_end' : '2018-04-19 00:00:00',
    'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
    'buy': '1-sellEnd_1open*1.0001',
    'sell': 'buy-10_realHighest',
    'filter': 'filter1',
    'f1_above_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'f1_above_indicator': 'SMA',
    'f1_above_average': '30',
    'f1_below_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'f1_below_indicator': 'SMA',
    'f1_below_average': '7',
    'pattern': 'pattern1',
    'p1_threshold' : '30',
    'p2_td_s': '-9',
    'p3_td_c': '13',
    'max_order': '500', # in USD
    }
    
    goodtimes = frontDoor(p)
    pprint(goodtimes)

def frontDoor(p):
    # lineBellow_all and lineAbove_all are both arrays of shape (<num_of_candles>,2).
    # The first column is filled with timestamp values and the second one with SMA or EMA
    # values, depending upon which option was chosen at p['chart_filter'][1]['lineAbove']['indicator']
    # and p['chart_filter'][1]['lineBellow']['indicator'].
    # The arrays will contain the timestamp and average of every candle existing inside
    # p['f1_below_path_candle_file'] for lineBellow and 
    # p['f1_above_path_candle_file'] for lineAbove. 

    trade_candle_df = get_dataframe(p["path_candle_file"])
    candle_sec = trade_candle_df.iloc[1].name - trade_candle_df.iloc[0].name
    ma_candle_df = get_dataframe(p["f1_below_path_candle_file"])
    candle_sec_ma = ma_candle_df.iloc[1].name - ma_candle_df.iloc[0].name

    lineBellow_all = getattr(momentum_indicators,p['f1_below_indicator'].lower())(p['f1_below_path_candle_file'],int(p['f1_below_average']))
    lineAbove_all = getattr(momentum_indicators,p['f1_above_indicator'].lower())(p['f1_above_path_candle_file'],int(p['f1_above_average']))
    lineAbove = filterbydate_array(lineAbove_all,(p['timeframe_start'],p['timeframe_end']))
    lineBellow = filterbydate_array(lineBellow_all,(p['timeframe_start'],p['timeframe_end']))
    filtered_array = lineAbove[lineAbove[:,1]>lineBellow[:,1],0]   
    goodtimes = buildPeriods(filtered_array,candle_sec,candle_sec_ma)
    return goodtimes

def buildPeriods(filtered_array,candle_sec,candle_sec_ma):
    goodtimes = []
    tsdiff_array = np.diff(filtered_array)
    candlediff_array = tsdiff_array/candle_sec_ma
    filtered_array = np.append(filtered_array,100)
    candlediff_array = np.append(candlediff_array,100)
    start = filtered_array[0]
    for index in range(filtered_array.shape[0]-1):
        if candlediff_array[index] == 1:
            continue
        elif candlediff_array[index] > 1:
            goodtimes.append([start,filtered_array[index]])
        start = filtered_array[index+1]
    return goodtimes

def get_dataframe(candle_file):
    pre_candles_df = pd.read_csv(candle_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])
    candles_df = pre_candles_df.set_index('timestamp')
    return candles_df

def filterbydate_array(array,timeframe):
    # Input: <array> is a array to be filtered and <timeframe> a list with two strings, the 
    # first being the inferior limit of the timeframe and the second its superior limit.
    # Output: An array within the boundaries of the limits described in <timeframe>. The
    # boundaries are inclusive, meaning both limits are inside this partition.
    # Info: It works in a similar way of filterbydate_df function, but instead of slicing a
    # dataframe this function slices an array.
    struct_time0 = time.strptime(timeframe[0], '%Y-%m-%d %H:%M:%S')
    struct_time1 = time.strptime(timeframe[1], '%Y-%m-%d %H:%M:%S')
    inferior = calendar.timegm(struct_time0)
    superior = calendar.timegm(struct_time1)
    try:
        array_partition = array[(array[:,0] >= inferior) & (array[:,0] <= superior)]
        return array_partition
    except:
        print('\nYou picked a bad timeframe mate.')

def filterbydate_df(df,timeframe):
    # Input: <df> is a dataframe to be filtered and <timeframe> a list with two strings, the 
    # first being the inferior limit of the timeframe and the second its superior limit.
    # Output: A dataframe within the boundaries of the limits described in <timeframe>. The
    # boundaries are inclusive, meaning both limits are inside this partition.
    struct_time0 = time.strptime(timeframe[0], '%Y-%m-%d %H:%M:%S')
    struct_time1 = time.strptime(timeframe[1], '%Y-%m-%d %H:%M:%S')
    inferior = calendar.timegm(struct_time0)
    superior = calendar.timegm(struct_time1)
    try:
        df_partition = df[(df.timestamp >= inferior) & (df.timestamp <= superior)]
        df_partition.index = range(len(df_partition.index))
        return df_partition
    except:
        print('\nYou picked a bad timeframe mate.')

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))
