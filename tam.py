import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,sys,os
from pprint import pprint
import chart_filter, unit_maker
import matplotlib.pyplot as plt
from scipy import stats

def main():
    p = {
        'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
        'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
        'buy' : {'trigger': ['1'],'moment_index':'open'},
        'sell' : {'trigger': ['4'],'moment_index':'high'},
        'target': '0.007',
        'chart_filter': {
            'toggle': True,
            'condition': '1',
            'path_trendline_file': 'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
            'mode': 'less_than_limit',
            'condition_parameter': 'm',
            'limit': 0,
            'limit1': 0,
            'limit2': 0
        },
        'unit_maker': {
            'threshold' : 30,
            'td_s': 4
        },
        }

    export_multiple_events(p)

# --------------------------------------------------------------------------------------------------------
# * SECTION 1 *
# Here is the place we have functions that manages event creation. 

def print_event(p):
    goodtimes = chart_filter.callable(p)
    units_list = unit_maker.callable(p,goodtimes)
    report = scheme1(p,units_list)
    pprint(report)

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
    report = scheme1(p,units_list)
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
    iter_list = [['3'],['4'],['5'],['6'],['8'],['9'],['10'],['11'],['12'],['13'],['14']]
    for item in iter_list:
        p['sell']['trigger'] = item 
        export_multiple_events(p)

# --------------------------------------------------------------------------------------------------------
# * SECTION 2 *
# Here are functions that can automate event creations and some other processes.

def scheme1(p,units_list):
    unit_profit = []
    unit_lowest = []

    for unit in units_list:
        profit = (unit[p['sell']['trigger'][0]]['high'] - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open']
        lowest = (min(unit[item]['high'] for item in unit.keys() if item != '0') - unit[p['buy']['trigger'][0]]['open']) / unit[p['buy']['trigger'][0]]['open']
        unit_lowest.append(lowest)
        unit_profit.append(profit)

    report = {
        'target': p['target'],
        'overtarget': 100 - stats.percentileofscore(unit_profit,float(p['target'])),
        'unit_amount': len(unit_profit),
    }
    
    return report

# --------------------------------------------------------------------------------------------------------
# * SECTION 3 *
# Place for random functions that may or may not be called somewhere in the code.

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
    with open(path, 'w') as outfile:
        json.dump(data, outfile)  

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Runtime: ',time2-time1)