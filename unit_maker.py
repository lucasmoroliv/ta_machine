import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys,operator
from pprint import pprint
from builders import momentum_indicators 
import chart_filter

def main():
    p = {
    'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'timeframe' : ['2014-01-01 00:00:00','2018-04-19 00:00:00'],
    'candle_sec': '1800',
    # 'buy': '1-2-3-4-5_0high',
    'buy': '1_1open*1.0001',
    'sell': 'buy-10_realHighest',
    'chart_filter': {
        'toggle': False,
        'condition': 'condition1',
        'path_trendline_file': 'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_150_4_15_001_001_4.txt', 
        'mode': 'less_than_limit',
        'condition_parameter': 'm',     
        'limit': '0',
        'limit1': '0',
        'limit2': '0'
    },
    'unit_maker': {
        'threshold' : '30',
        'pattern': 'pattern1',
        'candle_features': ['open','high','low','close'],
    },
    'tam': {
        'scheme': 'scheme4',
        'max_order': '5',
        'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
    }
    }

    goodtimes = chart_filter.callable(p)
    units_list = callable(p,goodtimes)
    pprint(units_list)

def callable(p,goodtimes):
    candle_df = get_dataframe(p)
    raw_df = get_raw(p)
    rsi_df = get_rsi_df(p)
    td_s_df = get_td_s_df(p)
    td_c_df = get_td_c_df(p)
    units_list = globals()[p['unit_maker']['pattern']](p,goodtimes)
    
    add_buy(p,units_list,candle_df,raw_df)
    # add_candles(p,units_list,candle_df,rsi_df,td_s_df,td_c_df)
    add_sell(p,units_list,candle_df,raw_df)
    add_lowest(p,units_list,candle_df,raw_df)
    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 1 *
# Each one of the functions in this section must return a units_list. 

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
# Add details of relevant candles to units_list for further analysis.

def add_candles(p,units_list,candle_df,rsi_df,td_s_df,td_c_df):
    candle_features = p['unit_maker']['candle_features'] 

    for unit in units_list:
        unit_ts = unit['0']['ts']
        for candle in range(0,5+1):
        # for candle in range(int(unit['buy']['candle'][0]),5+1):
            candle_ts = unit_ts + candle * int(p['candle_sec'])
            if candle != 0:
                unit[str(candle)] = {}
            for feature in candle_features:
                unit[str(candle)][feature] = candle_df.loc[candle_ts][feature]

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
    for unit in units_list:
        unit['buy'] = {}
        find_buy(p,unit,candle_df,raw_df,operator_dict)

def add_sell(p,units_list,candle_df,raw_df):
    candle,moment = translate_order('sell',p['sell'])
    p['sell'] = {
        'candle': candle,
        'moment': moment
    }
    for unit in units_list:
        if 'first_executed' in unit['buy']:
            unit['sell'] = {}
            find_sell(p,unit,candle_df,raw_df)

def add_lowest(p,units_list,candle_df,raw_df):
    for unit in units_list:
        if 'first_executed' in unit['buy']:
            if 'last_executed' in unit['sell']:
                unit['lowest'] = {}
                find_lowest(p,unit,candle_df,raw_df)

# ---------------------------------------------------------------------------------
# * SECTION 3 *
# Here is a space to store all sorts of auxiliary functions that will help the pattern
# funcions to find their units_list.

def find_buy(p,unit,candle_df,raw_df,operator_dict):
# Getting the price from the dataframe candle_df.
    unit['buy']['price'] = candle_df.loc[int(unit['0']['ts'])+int(p['candle_sec'])*int(p['buy']['moment']['candle'])][p['buy']['moment']['ohlc']]
# Altering the unit['buy']['price'] with the p['buy']['moment']['change'] in case p['buy']['moment']['operator'] exists.
    if 'operator' in p['buy']['moment']:
        unit['buy']['price'] = operator_dict[p['buy']['moment']['operator']](float(unit['buy']['price']),float(p['buy']['moment']['change']))  
# start_interval value is equal the first timestamp of p['buy']['candle'][0]. The buy event can start from here on.
    start_interval = int(unit['0']['ts'])+int(p['candle_sec'])*int(p['buy']['candle'][0])
# end_interval value is equal the first timestamp of p['buy']['candle'][-1] + 1. 
    end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(p['buy']['candle'][-1])+1) 
# raw_section is a dataframe that has all the rows of raw_df that are within the start_interval and end_interval 
# limits. It is worth it pointing out that the first statement is >= and the second is only < because the latter 
# doesn't want to include the rows with timestamp of end_interval in the dataframe. 
    raw_section = raw_df[(raw_df.timestamp>=start_interval) & (raw_df.timestamp<end_interval)]    
# raw_section2 is a dataframe with all the rows of raw_section that has the value price greater than of or equal 
# unit['buy']['price'].
    raw_section2 = raw_section[raw_section.price>=unit['buy']['price']]

# A new column named 'acc_volume' is added to raw_section2.
    pd.options.mode.chained_assignment = None
    raw_section2['acc_volume'] = raw_section2['volume'].cumsum(axis = 0)
# It checks if raw_section2 has once an accumulated volume of at least float(p['tam']['max_order']). 
    if (raw_section2.acc_volume >= float(p['tam']['max_order'])).any():
    # 'row' is the first row of raw_section2 that has accumulated volume greater than or equal to float(p['tam']['max_order']).
        row = raw_section2[raw_section2.acc_volume >= float(p['tam']['max_order'])]
        row = row.iloc[0]
        unit['buy']['first_executed'] = {
            'ts': raw_section2.iloc[0].timestamp,
            'index': raw_section2.iloc[0].name
        }
        unit['buy']['last_executed'] = {
            'ts': row.timestamp,
            'index': row.name
        }

def find_sell(p,unit,candle_df,raw_df):
# In order to find raw_section at this function we can't simple get the first timestamp of the buy candle,
# or more precisely p['buy']['candle'][0], because we didn't buy anything there! That value only indicated
# that we could have our buy event FROM that time, and that event should happens only until p['buy']['candle'][1].
# The inferior limit to define the raw_section of this function (raw_section here is the partition of each unit 
# where the sell event can happen), should be one value that represents the very moment we get our whole order 
# executed and are in trade. This value can't be a timestamp though, because it can indicate lots of moments since 
# raw_df shows us that in a single second we can see different trades. If we want to get some value that 
# represents this moment where we are fully in trade, we need to grab the index of this row. And by the way, it
# out that the start_index should be unit['buy']['last_executed']['index'], because if we do that we are allowing
# the sell event to happen at this moment too.  
    start_index = unit['buy']['last_executed']['index'] + 1
# The end_interval value is going to be in this case the first timestamp of the candle after p['buy']['candle'][-1].
    end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(p['buy']['candle'][-1])+1)
    raw_section = raw_df[(raw_df.index>=start_index) & (raw_df.timestamp<end_interval)]    
    executed_sofar = 0
# Sort the raw_section in a way the row with the highest price is on top and row with lowest price in on the
# bottom. Also, in case of rows with same price, the ones with smaller indexes will be on top. That's important,
# because the rows with lower indexes will be executed first than the ones with higher indexes.
    raw_sorted = raw_section.sort_values(by=['price'],ascending=False,kind='mergesort')
    # raw_sorted.reset_index(inplace=True,drop=True)
# Iterate through the rows until executed_sofar is greater than or equal to p['tam']['max_order'].
    i = 0
    for index,row in raw_sorted.iterrows():
        executed_sofar = executed_sofar + row.volume
        if executed_sofar >= float(p['tam']['max_order']):
# The following condition was added because the units that have the previous condition met at the first iteration
# can't create 'until_i' correctly, because 'i' in such case has value 0 and raw_sorted.iloc[0:0] gives error.
# With that said, when 'i' is equal to 0 (first iteration) greater_ts_row is created differently.   
            if i == 0:
                greater_ts_row = row
            else:
# This next dataframe is a partition of raw_sorted that represents the part of it the program covered up to this
# iteration.
                until_i = raw_sorted.iloc[0:i]
# Next, we get the row with highest value of timestamp in until_i.
                greater_ts_row = until_i[until_i.timestamp == until_i.timestamp.max()].iloc[-1]
# Attention, that's not the price paid by the last execution order that happens at unit['sell']['last_executed'].
# This price is lower than or equal to this value. The concept of realHighest is quite hard to explain it here with
# some few words, but essentially is: The higher price target we can add to the order book that will execute the
# p['tam']['max_order'] amount of bitcoins.
            unit['sell']['realHighest'] = row.price
            unit['sell']['last_executed'] = {
                'ts': greater_ts_row.timestamp, 
                'index': greater_ts_row.name 
            }
            break 
        i = i + 1

def find_lowest(p,unit,candle_df,raw_df):
# The inferior and superior limits to define the unit_section dataframe will be both indexes. This is because
# timestamp information can't represent the exact order executed for the buy or sell event. The good way to 
# represent them is to use indexes, which can be thought as rows IDs.
    start_index = unit['buy']['first_executed']['index']
    end_index = unit['sell']['last_executed']['index']
    raw_section = raw_df[start_index:end_index]    
# The variable min_row receives the row with the lowest price within raw_section.
    min_row = raw_section[raw_section.price == raw_section.price.min()].iloc[0]
    unit['lowest']['price'] = min_row.price
    unit['lowest']['ts'] = min_row.timestamp
    unit['lowest']['index'] = min_row.name

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
        ope = [i for i in ['+','-','-'] if i in moment['string']]
        if ope != []:
            moment['operator'] = ope[0]
            moment['change'] = moment['string'][moment['string'].find(moment['operator'])+1:]
        return candle,moment

    if mode == 'sell':
        return candle,moment

def get_raw(p):
    return pd.read_csv(p['tam']['path_historical_data'], header=None, names=['timestamp','price','volume'])

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

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))

