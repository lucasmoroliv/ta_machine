import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,sys
from pprint import pprint
import chart_filter, unit_maker
import matplotlib.pyplot as plt
from scipy import stats

def main():
    p = {
        'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
        'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
        'buy' : {'trigger': ['1'],'moment_index':'open'},
        'sell' : {'trigger': ['6'],'moment_index':'high'},
        'target': '0.01',
        'chart_filter': {
            'toggle': False,
            'condition': '1',
            'path_trendline_file': 'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
            'mode': 'greater_than_limit',
            'condition_parameter': 'm',
            'limit': 0,
            'limit1': 0,
            'limit2': 0
        },
        'unit_maker': {
            'threshold' : 30,
        },
        }
    single_event(p)

# --------------------------------------------------------------------------------------------------------
# * SECTION 1 *
# Here is the place we have functions that manages event creation. 

def single_event(p):
    
    goodtimes = chart_filter.callable(p)
    units_list = unit_maker.callable(p,goodtimes) 
    report = scheme1(p,units_list)
    pprint(report)

def multiple_events(p):
    pass


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
        'rsi_threshold' : p['unit_maker']['threshold'],
        'profit_stats': {
            'target': p['target'],
            'overtarget': stats.percentileofscore(unit_profit,float(p['target'])),
            'unit_amount': len(unit_profit)
        }
    }
            # 'max': np.max(unit_profit),
            # 'min': np.min(unit_profit),
            # 'median': np.median(unit_profit),
            # 'mean': np.mean(unit_profit),
            # '25th percentile': np.percentile(unit_profit,25),
            # '50th percentile': np.percentile(unit_profit,50),
            # '75th percentile': np.percentile(unit_profit,75),
            # },
        # 'omega_lowest_stats': {
            # 'stop': p['stop'],
            # 'overstop': stats.percentileofscore(omega_unit_lowest,p['target']) 
            # 'max': np.max(unit_lowest),
            # 'min': np.min(unit_lowest),
            # 'median': np.median(unit_lowest),
            # 'mean': np.mean(unit_lowest),
            # '25th percentile': np.percentile(unit_lowest,25),
            # '50th percentile': np.percentile(unit_lowest,50),
            # '75th percentile': np.percentile(unit_lowest,75),
            # },
        # 'overtarget_lowest_stats': {
            # 'stop': p['stop'],
            # 'overstop': stats.percentileofscore(overtarget_unit_lowest,p['target']) 
            # }
    # }

    return report

# --------------------------------------------------------------------------------------------------------
# * SECTION 3 *
# Place for random functions that may or may not be called somewhere in the code.

def histogram(array,resolution):
    plt.hist(array,resolution)
    plt.show()

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Runtime: ',time2-time1)