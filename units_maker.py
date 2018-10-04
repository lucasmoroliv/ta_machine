import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys,operator,os
from pprint import pprint
from builders import momentum_indicators 
import chart_filter
pd.options.mode.chained_assignment = None


def main():
    p = {
    'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'timeframe' : ['2014-01-01 00:00:00','2018-04-19 00:00:00'],
    'candle_sec': '1800',
    'buy': '1-sellEnd_1open*1.0001',
    'sell': 'buy-10_realHighest',
    'chart_filter': {
        'toggle': True,
        'condition': 'condition1',
        'path_trendline_file': 'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_150_4_15_001_001_4.txt', 
        'mode': 'greater_than_limit',
        'condition_parameter': 'm',     
        'limit': '0',
        'limit1': '0',
        'limit2': '0'
    },
    'unit_maker': {
        'threshold' : '30',
        'pattern': 'pattern1',
        'candle_features': ['open','high','low','close'],
        'max_order': '500', # in USD
        'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
        'add': ['buy','sell','lowest'] 
    }
    }

    goodtimes = chart_filter.callable(p)
    units_list = callable(p,goodtimes)
    pprint(units_list)
    write_json((p,units_list))

def callable(p,goodtimes):
    candle_df = get_dataframe(p)
    raw_df = get_raw(p)
    # rsi_df = get_rsi_df(p)
    # td_s_df = get_td_s_df(p)
    # td_c_df = get_td_c_df(p)
    units_list = globals()[p['unit_maker']['pattern']](p,goodtimes)
    for item in p['unit_maker']['add']:
        globals()['add_{0}'.format(item)](p,units_list,candle_df,raw_df)
    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 1 *
# Every function in this section must return a units_list, with the timestamp of the candle 0 of each unit. 

def pattern1(p,goodtimes):
    rsi = momentum_indicators.rsi(p['path_candle_file'])
    units_list = []
    threshold = float(p['unit_maker']['threshold'])
    if isinstance(goodtimes, np.ndarray):
        for index in range(goodtimes.shape[0]):
            ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
            mini_rsi = filter_rsi(rsi,ts_timeframe)
            for i in range(mini_rsi.shape[0])[:-1]:
                if mini_rsi[i,1] < threshold and mini_rsi[i-1,1] > threshold:
                    units_list.append({'0': {'ts': mini_rsi[i,0]}})
    else:       
        ts_timeframe = [calendar.timegm(time.strptime(p['timeframe'][0], '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe'][1], '%Y-%m-%d %H:%M:%S'))]
        mini_rsi = filter_rsi(rsi,ts_timeframe) 
        for i in range(mini_rsi.shape[0])[:-1]:
            if mini_rsi[i,1] < threshold and mini_rsi[i-1,1] > threshold:
                units_list.append({'0': {'ts': mini_rsi[i,0]}})
    return units_list

def pattern2(p,goodtimes):
    # For td_setup : equal to 9 for "normal" td_sell_setup, 80 for minimal_sell_setup or 90 for perfect_sell_setup
    #              : equal to -9 for "normal" td_buy_setup, -80 for minimal_buy_setup or -90 for perfect_sell_setup
    td_s_df = get_td_s_df(p)
    td_s_df = td_s_df.reset_index()
    td = td_s_df.values
    td_s = int(p['unit_maker']['td_s'])
    units_list = []
    if isinstance(goodtimes, np.ndarray):
        for index in range(goodtimes.shape[0]):
            ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
            mini_td = filter_td(td,ts_timeframe)
            for i in range(mini_td.shape[0])[:-1]:
                if mini_td[i,1]==td_s:
                    units_list.append({'0': {'ts': mini_td[i,0]}})
    else:
        ts_timeframe = [calendar.timegm(time.strptime(p['timeframe'][0], '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe'][1], '%Y-%m-%d %H:%M:%S'))]
        mini_td = filter_td(td,ts_timeframe)
        for i in range(mini_td.shape[0])[:-1]:
            if mini_td[i,1]==td_s:
                units_list.append({'0': {'ts': mini_td[i,0]}})
    return units_list

def pattern3(p,goodtimes):
    # For td_countdown : equal to 13 for td_sell_countdown
    #                  : equal to -13 for td_buy_countdown
    td_c_df = get_td_c_df(p)
    td_c_df = td_c_df.reset_index()
    td = td_c_df.values
    td_c = int(p['unit_maker']['td_c'])
    units_list = []
    if isinstance(goodtimes, np.ndarray):
        for index in range(goodtimes.shape[0]):
            ts_timeframe = (goodtimes[index,0],goodtimes[index,1])
            mini_td = filter_td(td,ts_timeframe)
            for i in range(mini_td.shape[0])[:-1]:
                if mini_td[i,1]==td_c:
                    units_list.append({'0': {'ts': mini_td[i,0]}})
    else:
        ts_timeframe = [calendar.timegm(time.strptime(p['timeframe'][0], '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe'][1], '%Y-%m-%d %H:%M:%S'))]
        mini_td = filter_td(td,ts_timeframe)
        for i in range(mini_td.shape[0])[:-1]:
            if mini_td[i,1]==td_c:
                units_list.append({'0': {'ts': mini_td[i,0]}})
    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 2 *
# Add details to units_list for further analysis.

def add_buy(p,units_list,candle_df,raw_df):
    operator_dict = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul
    }
    candle,moment = translate_order('buy',p['buy'])
    p['buy'] = {
        'candle': candle,
        'moment': moment
    }
    candle,moment = translate_order('sell',p['sell'])
    p['sell'] = {
        'candle': candle,
        'moment': moment
    }
    for unit in units_list:
        unit['buy'] = {}
        find_buy(p,unit,candle_df,raw_df,operator_dict)

def add_sell(p,units_list,candle_df,raw_df):
    for unit in units_list:
        if unit['buy']['type'] == 'all-bought':
            unit['sell'] = {}
            find_sell(p,unit,candle_df,raw_df)

def add_lowest(p,units_list,candle_df,raw_df):
    for unit in units_list:
        if unit['buy']['type'] == 'all-bought':
            if unit['sell']['type'] == 'all-sold':
                unit['lowest'] = {}
                find_lowest(p,unit,candle_df,raw_df)

# ---------------------------------------------------------------------------------
# * SECTION 3 *
# Here is a space to store all sorts of auxiliary functions.

def find_buy(p,unit,candle_df,raw_df,operator_dict):
    unit['buy']['price'] = candle_df.loc[int(unit['0']['ts'])+int(p['candle_sec'])*int(p['buy']['moment']['candle'])][p['buy']['moment']['ohlc']]
    if 'operator' in p['buy']['moment']:
        unit['buy']['price'] = operator_dict[p['buy']['moment']['operator']](float(unit['buy']['price']),float(p['buy']['moment']['change']))  
    start_interval = int(unit['0']['ts'])+int(p['candle_sec'])*int(p['buy']['candle'][0])
    if p['buy']['candle'][-1] == 'sellEnd':
        end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(p['sell']['candle'][-1])+1)
    else:
        end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(p['buy']['candle'][-1])+1) 
    raw_section = raw_df[(raw_df.timestamp>=start_interval) & (raw_df.timestamp<end_interval)]    
    lowest_of_section = raw_section[raw_section.price == raw_section.price.min()].iloc[0]
    unit['buy']['lowest'] = {
        'ts': int(lowest_of_section.timestamp), 
        'index': int(lowest_of_section.name),
        'price': (float(lowest_of_section.price) - unit['buy']['price'])/unit['buy']['price']
    }
    raw_partition = raw_section[raw_section.price>=unit['buy']['price']]
    if raw_partition.empty:
        unit['buy']['type'] = 'nothing-bought'
        return
    raw_partition['USD_acc_volume'] = raw_partition['volume'].cumsum(axis = 0)*raw_partition['price']
    unit['buy']['first_executed'] = {
        'ts': int(raw_partition.iloc[0].timestamp),
        'index': int(raw_partition.iloc[0].name)
    }
    if (raw_partition.USD_acc_volume >= float(p['unit_maker']['max_order'])).any():
        unit['buy']['type'] = 'all-bought'
        last_executed_row = raw_partition[raw_partition.USD_acc_volume >= float(p['unit_maker']['max_order'])].iloc[0]
        unit['buy']['last_executed'] = {
            'ts': int(last_executed_row.timestamp),
            'index': int(last_executed_row.name)
        }
        start_interval_to_last_executed = raw_section.loc[:unit['buy']['last_executed']['index']]
        lowest_row = start_interval_to_last_executed[start_interval_to_last_executed.price == start_interval_to_last_executed.price.min()].iloc[0]
        unit['buy']['lowest'] = {
            'ts': int(lowest_row.timestamp), 
            'index': int(lowest_row.name),
            'price': (float(lowest_row.price) - unit['buy']['price'])/unit['buy']['price']
        }
    else:
        unit['buy']['type'] = 'partially-bought'

    

def find_sell(p,unit,candle_df,raw_df):
    start_index = unit['buy']['last_executed']['index']
    end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(p['sell']['candle'][-1])+1)
    raw_section = raw_df[(raw_df.index>start_index) & (raw_df.timestamp<end_interval)]    
    raw_sorted = raw_section.sort_values(by=['price'],ascending=False)
    
    if raw_sorted.empty:
        unit['sell']['type'] = 'nothing-sold'
        return
    else:
        unit['sell']['type'] = 'partially-sold'
        raw_sorted['USD_acc_volume'] = raw_sorted['volume'].cumsum(axis = 0)*raw_sorted['price']

    if (raw_sorted.USD_acc_volume >= float(p['unit_maker']['max_order'])).any():
        unit['sell']['type'] = 'all-sold'
        realHighest_price = raw_sorted[raw_sorted.USD_acc_volume >= float(p['unit_maker']['max_order'])].iloc[0].price
        unit['sell']['realHighest_price'] = realHighest_price
        unit['sell']['realHighest'] = (float(realHighest_price) - unit['buy']['price'])/unit['buy']['price']

        raw_partition = raw_section[raw_section.price>=realHighest_price]
        raw_partition['USD_acc_volume'] = raw_partition['volume'].cumsum(axis = 0)*raw_partition['price']
        last_row = raw_partition[raw_partition.USD_acc_volume >= float(p['unit_maker']['max_order'])].iloc[0]
        unit['sell']['first_executed'] = {
            'ts': int(raw_partition.iloc[0].timestamp), 
            'index': int(raw_partition.iloc[0].name) 
        }
        unit['sell']['last_executed'] = {
            'ts': int(last_row.timestamp), 
            'index': int(last_row.name) 
        }

def find_lowest(p,unit,candle_df,raw_df):
    start_index = unit['buy']['last_executed']['index'] + 1
    end_index = unit['sell']['last_executed']['index']
    raw_section = raw_df.loc[start_index:end_index]    
    min_row = raw_section[raw_section.price == raw_section.price.min()].iloc[0]
    unit['lowest']['price'] = (float(min_row.price) - unit['buy']['price'])/unit['buy']['price']
    unit['lowest']['ts'] = int(min_row.timestamp)
    unit['lowest']['index'] = int(min_row.name)

def translate_order(mode,input):
# This function receives as input a string with the format '1-2-3_0high+30' and returns a list called 'candle' and
# a dictionary 'moment' that are useful for further calculation.
    moment = {}
    candle,moment['string'] = input.split('_')
    candle = candle.split('-')

    if mode == 'buy':
        index = 0
        for char in moment['string']:
            if char.isdigit():
                index = index + 1 
            else:
                break
        moment['candle'] = moment['string'][0:index]
        moment['ohlc'] = [i for i in ['open','high','low','close'] if i in moment['string']][0]
        ope = [i for i in ['+','-','*'] if i in moment['string']]
        if ope != []:
            moment['operator'] = ope[0]
            moment['change'] = moment['string'][moment['string'].find(moment['operator'])+1:]
        return candle,moment

    if mode == 'sell':
        return candle,moment

def get_raw(p):
    return pd.read_csv(p['unit_maker']['path_historical_data'], header=None, names=['timestamp','price','volume'])

def filter_rsi(rsi,timeframe):
    return rsi[(rsi[:,0] >= timeframe[0]) & (rsi[:,0] <= timeframe[1])]

def filter_td(td,timeframe):
    return td[(td[:,0] >= timeframe[0]) & (td[:,0] <= timeframe[1])]

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
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        td_s_data = np.array(big_list)
        td_s_data = td_s_data.astype(int)
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
        td_c_data = td_c_data.astype(int)
    td_c_df = pd.DataFrame(td_c_data, columns = ['timestamp','td_c'])
    td_c_df = td_c_df.set_index('timestamp')
    return td_c_df

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    half1_path = 'builders/warehouse/setup_data/setup'
    half2_path = str(int(time.time()))
    path = half1_path + half2_path + '.txt'
    while os.path.exists(path):
        time.sleep(1)
        half2_path = str(int(time.time()))
        path = half1_path + half2_path + '.txt'
    with open(path, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))
