import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,sys,os
from pprint import pprint
import chart_filter, unit_maker

def main():
# --------------------------------------------------------------------------------------------------------
# * MAIN *
# In order to create an event you must fill in the parameters dictionary below. 
    
    p = {
        'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
        'timeframe' : ['2014-01-01 00:00:00','2018-04-19 00:00:00'],
        'candle_sec': '1800',
        # 'buy' : {'trigger': ['1'],'moment_index':'open'},
        # 'sell' : {'trigger': ['10'],'moment_index':'high'},
        # 'target': '0.007',
        'buy': '1_1open',
        'sell': 'realHighest',
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
            'start_candle': '0',
            'end_candle': '20',
            # 'candle_features': ['open','high']
            'candle_features': []
        },
        'tam': {
            'scheme': 'scheme4',
            'min_volume_over_target': '10',
            'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
        }
        }

# --------------------------------------------------------------------------------------------------------
# * MAIN *
# This is the place you call the function to create the event report. 

    print_event(p)

# --------------------------------------------------------------------------------------------------------
# * SECTION 1 *
# Here is the place we put functions that manage event creation. 

def print_event(p):
    goodtimes = chart_filter.callable(p)
    units_list = unit_maker.callable(p,goodtimes)
    # report = globals()[p['tam']['scheme']](p,units_list)
    # pprint(report)
    pprint(units_list)

def print_multiple_events(p):
    print('---------------------------------------------------------------------------')
    iter_list = [i for i in range(0,100+1)]  
    for item in iter_list:
        p['unit_maker']['threshold'] = item
        print_event(p)
        print('---------------------------------------------------------------------------')

def return_event(p):
    goodtimes = chart_filter.callable(p)
    units_list = unit_maker.callable(p,goodtimes)
    report = globals()[p['tam']['scheme']](p,units_list)
    return report

def export_multiple_events(p):
    iter_data = {}
    iter_data['p'] = p
    iter_list = [i for i in range(0,100+1)]  
    for item in iter_list:
        p['unit_maker']['threshold'] = item
        report = return_event(p)
        iter_data[str(p['unit_maker']['threshold'])] = report
    write_json(iter_data)    

def superbot(p):
    # This function run the function export_multiple_events changing some of the "p" parameters
    # it receives as argument.
    iter_list = [
        'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
        'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_400_4_15_0015_001_8.txt',
        'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_80_400_4_15_001_001_8.txt',
        'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_80_500_3_15_0005_001_8.txt'
    ]
    export_multiple_events(p)
    p['chart_filter']['toggle'] = True
    for item in iter_list:
        p['chart_filter']['path_trendline_file'] = item 
        export_multiple_events(p)

# --------------------------------------------------------------------------------------------------------
# * SECTION 2 *
# Here are functions that can automate event creations and some other processes.

def scheme1(p,units_list):
    unit_profit = []
    unit_lowest = []

    for unit in units_list:
        profit = (unit[p['sell']['trigger'][0]]['high'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open']
        lowest = (min(unit[item]['low'] for item in unit.keys() if item != '0') - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open']
        unit_lowest.append(lowest)
        unit_profit.append(profit)

    report = {
        'overtarget': 100 - stats.percentileofscore(unit_profit,float(p['target'])),
        'unit_amount': len(units_list),
    }
    
    return report

def scheme2(p,units_list):
    
    unit_highest = []
    unit_lowest = []
    highest_candle_list = []
    lowest_candle_list = []

    for unit in units_list:
        high_list = [(unit[str(candle)]['high'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open'] for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][0])+1)]
        highest = max(high_list) 
        highest_candle = int(p['buy']['trigger'][0]) + high_list.index(highest)  
        low_list = [(unit[str(candle)]['low'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open'] for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][0])+1)]
        lowest = min(low_list)
        lowest_candle = int(p['buy']['trigger'][0]) + low_list.index(lowest)
        unit_highest.append(highest)
        unit_lowest.append(lowest)
        highest_candle_list.append(str(highest_candle))
        lowest_candle_list.append(str(lowest_candle))
        
    report = {
        'overtarget': 100 - stats.percentileofscore(unit_highest,float(p['target'])),
        'unit_amount': len(units_list),
        'lowest_candle': {},
        'highest_candle': {}
    }

    for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][0])+1):
        report['lowest_candle'][candle] = lowest_candle_list.count(str(candle))
        report['highest_candle'][candle] = highest_candle_list.count(str(candle))

    return report

def scheme3(p,units_list):
    
    omega_highest = []
    omega_lowest = []

    for unit in units_list:
        high_list = [(unit[str(candle)]['high'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open'] for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][0])+1)]
        highest = max(high_list) 
        low_list = [(unit[str(candle)]['low'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open'] for candle in range(int(p['buy']['trigger'][0]),int(p['sell']['trigger'][0])+1)]
        lowest = min(low_list)
        omega_highest.append(highest)
        omega_lowest.append(lowest)
    report = {
        'omega_highest': omega_highest,
        'omega_lowest': omega_lowest,
        'unit_amount': len(units_list),
        'p': p
    }
    return report

def scheme4(p,units_list):
    pass
    # for unit in units_list:
    #     ts_reference = unit['0']['ts']
    #     start_unit =     
    
    
    
    
    
    
    



# --------------------------------------------------------------------------------------------------------
# * SECTION 3 *
# Place for random functions that may or may not be called somewhere in the code.

def get_volume_over_price(df,candle_sec,ts_candle0,candle,price):
    # This function gets the volume over the price of the specified candle.
    candle_start = ts_candle0 + candle * candle_sec 
    candle_end = candle_start + candle_sec
    candle_section = df.loc[candle_start:candle_end]
    print(candle_section)

def get_raw(p):
    pre_df = pd.read_csv(p['tam']['path_historical_data'], header=None, names=['timestamp','price','volume'])
    return pre_df.set_index('timestamp')

def histogram(array,resolution):
    plt.hist(array,resolution)
    plt.show()

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    half1_path = 'builders/warehouse/experiment_data/experiment'
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
    print('Runtime: ',time2-time1)
