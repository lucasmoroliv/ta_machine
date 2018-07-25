import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys
from pprint import pprint
from builders import momentum_indicators 
import matplotlib.pyplot as plt

def main():
    pass

def callable(p,goodtimes=None):
    candle_df = get_dataframe(p) 
    rsi_df = get_rsi_df(p)
    td_s_df = get_td_s_df(p)
    td_c_df = get_td_c_df(p)
    units_list = pattern2(p,goodtimes)
    fill_units_list(units_list,p,candle_df,rsi_df,td_s_df,td_c_df)

    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 1 *
# Each one of the functions in this section must return a units_list. 

def pattern1(p,goodtimes):
    rsi = momentum_indicators.rsi(p['path_candle_file'])
    units_list = []
    if isinstance(goodtimes, np.ndarray):
        for index in range(goodtimes.shape[0]):
            ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
            mini_rsi = filter_rsi(rsi,ts_timeframe)
            for i in range(mini_rsi.shape[0])[:-1]:
                if mini_rsi[i,1] < p['unit_maker']['threshold'] and mini_rsi[i-1,1] > p['unit_maker']['threshold']:
                    units_list.append({'0': {'ts': mini_rsi[i,0]}})
    else:       
        ts_timeframe = [calendar.timegm(time.strptime(p['timeframe'][0], '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe'][1], '%Y-%m-%d %H:%M:%S'))]
        mini_rsi = filter_rsi(rsi,ts_timeframe) 
        for i in range(mini_rsi.shape[0])[:-1]:
            if mini_rsi[i,1] < p['unit_maker']['threshold'] and mini_rsi[i-1,1] > p['unit_maker']['threshold']:
                units_list.append({'0': {'ts': mini_rsi[i,0]}})
    return units_list

def pattern2(p,goodtimes=None):
    # For td_setup : equal to 9 for "normal" td_sell_setup, 80 for minimal_sell_setup or 90 for perfect_sell_setup
    #              : equal to -9 for "normal" td_buy_setup, -80 for minimal_buy_setup or -90 for perfect_sell_setup
    td_s_df = get_td_s_df(p)
    td_s_pattern = td_s_df[td_s_df['td_s']==9]
    units_list =[]  
    candles0_array = td_s_pattern.index.tolist()
    for i in candles0_array:
        units_list.append({'0': {'ts': i}})
    return units_list

def pattern3(p,goodtimes=None):
    # For td_countdown : equal to 13 for td_sell_countdown
    #                  : equal to -13 for td_buy_countdown
    td_c_df = get_td_c_df(p)
    td_c_pattern = td_c_df[td_c_df['td_c']==13]
    units_list =[]
    candles0_array = td_c_pattern.index.tolist()
    for i in candles0_array:
        units_list.append({'0': {'ts': i}})
    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 2 *
# Add details of relevant candles to units_list for further analysis.

def fill_units_list(units_list,p,candle_df,rsi_df,td_s_df,td_c_df):
    candle_sec = candle_df.index[1] - candle_df.index[0]

    for act in ['buy','sell']:
        for unit in units_list:
            # for candle in p[act]['trigger']:
            for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][-1])+1):
                candle_ts = unit['0']['ts'] + candle * candle_sec
                unit[str(candle)] = {
                    'open': candle_df.loc[candle_ts]['open'],
                    'high': candle_df.loc[candle_ts]['high'],
                    'low': candle_df.loc[candle_ts]['low'],
                    'close': candle_df.loc[candle_ts]['close'],
                    'volume': candle_df.loc[candle_ts]['volume'],
                    'change': candle_df.loc[candle_ts]['change'],
                    'rsi': rsi_df.loc[candle_ts]['rsi'],
                    'td_s': td_s_df.loc[candle_ts]['td_s'],
                    'td_c': td_c_df.loc[candle_ts]['td_c']
                }

# ---------------------------------------------------------------------------------
# * SECTION 3 *
# Here is a space to store all sorts of auxiliary functions that will help the pattern
#  funcions to find thier units_list.

def filter_rsi(rsi,timeframe):
    return rsi[(rsi[:,0] >= timeframe[0]) & (rsi[:,0] <= timeframe[1])]

def get_dataframe(p):
    pre_candles_df = pd.read_csv(p['path_candle_file'], header=None, names=['time','timestamp','open','high','low','close','volume','change'])
    candles_df = pre_candles_df.set_index('timestamp')
    return candles_df

def get_rsi_df(p):
    rsi_array = momentum_indicators.rsi(p['path_candle_file'])
    pre_rsi_df = pd.DataFrame(rsi_array, columns = ['timestamp','rsi'])
    rsi_df = pre_rsi_df.set_index('timestamp')
    return rsi_df

def get_td_s_df(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open('builders/warehouse/td_data/td_setup_30min_bitstamp.csv', newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        list = []
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        td_s_data = np.array(big_list)
        td_s_data.astype(int)
    td_s_df = pd.DataFrame(td_s_data, columns = ['timestamp','td_s'])
    td_s_df = td_s_df.set_index('timestamp')
    return td_s_df

def get_td_c_df(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open('builders/warehouse/td_data/td_countdown_30min_bitstamp.csv', newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        list = []
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        td_c_data = np.array(big_list)
        td_c_data.astype(int)
    td_c_df = pd.DataFrame(td_c_data, columns = ['timestamp','td_c'])
    td_c_df = td_c_df.set_index('timestamp')
    return td_c_df

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Runtime: ',time2-time1)