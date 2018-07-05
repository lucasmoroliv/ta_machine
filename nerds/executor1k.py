import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib
from pprint import pprint

def main():
    p = {
    'path_candle_file' : '../warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv',
    'path_td_file': '../warehouse/td_data/' + 'td_setup_30min_bitstamp.csv',
    'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
    'start_candle' : -3,
    'end_candle' : 4,
    'buy' : {'candle':1,'moment':'open'},
    'sell' : {'candle':4,'moment':'high'},
    'target' : 0.01,
    'tourist_version': 'tourist1k',
    'digger_version': 'digger1k',
    'sculptor_version': 'sculptor1k',
    'researcher_version': 'researcher1'
    }
    callable(p)

def callable(p=None):
    tourist,digger,sculptor,researcher = import_module(p)
    goodtimes = tourist.callable(p)
    # print(goodtimes)
    candles0_array = digger.callable(goodtimes)
    # print(candles0_array)
    info_list = sculptor.callable(p,candles0_array)
    pprint(info_list)
    # result = researcher.callable(p,info_list)
    # pprint(result)

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
