import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib
from pprint import pprint

def main():
    p = {
    'path_candle_file' : '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv',
    'path_trendline_file': '../warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
    'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
    'start_candle' : -3,
    'end_candle' : 6,
    'buy' : {'candle':1,'moment':'open'},
    'sell' : {'candle':4,'moment':'high'},
    'target' : 0.007,
    'tourist_version': 'tourist1',
    'digger_version': 'digger1',
    'sculptor_version': 'sculptor3',
    'researcher_version': 'researcher1'
    }
    callable(p)

def callable(p=None):
    tourist,digger,sculptor,researcher = import_module(p)
    goodtimes = tourist.callable(p)
    candles0_array = digger.callable(p,goodtimes)
    info_list = sculptor.callable(p,candles0_array)
    result = researcher.callable(p,info_list)
    pprint(result)

def import_module(p):
    tourist = __import__(p['tourist_version'])
    digger = __import__(p['digger_version'])
    sculptor = __import__(p['sculptor_version'])
    researcher = __import__(p['researcher_version'])
    return tourist,digger,sculptor,researcher

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
