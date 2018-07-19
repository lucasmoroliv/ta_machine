import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,numbers
from pprint import pprint

def main():

    class event:

        def __init__(self,p):
            for key,value in p.items():
                setattr(self,key,value)

            for act in ['sell','buy']:
                if '-' in getattr(self,act)['candle']:
                    getattr(self,act)['candle'] = getattr(self,act)['candle'].split('-')

                # '1h*1.05','2rsi*1.04','4c-500'.
                ope_index = max([getattr(self,act)['moment'].find(mode) for mode in ['*','+','-']])
                if ope_index > 1:
                    string = getattr(self,act)['moment']
                    half1,half2 = string.split(string[ope_index])             
                    getattr(self,act)['moment'] = {} 
                    getattr(self,act)['moment']['mode'] = string[ope_index]  
                    getattr(self,act)['moment']['candle'],getattr(self,act)['moment']['feature'] = self.split_num_str(str(half1))
                    getattr(self,act)['moment']['value'] = half2 
                # '5000','3500','2000'. Yet to think about this one. Letting it here for further investigation.
                elif isinstance(getattr(self,act)['moment'], numbers.Number):
                    value = float(getattr(self,act)['moment'])
                    getattr(self,act)['moment'] = {}
                    getattr(self,act)['moment']['value'] = value
                    getattr(self,act)['moment']['mode'] = 'absolute'
                    getattr(self,act)['moment']['candle'] = 'any'
                    getattr(self,act)['moment']['feature'] = 'any'
                # '1h','2rsi','4c'  
                elif sum(char.isdigit() for char in getattr(self,act)['moment']) == 1:
                    string = getattr(self,act)['moment']
                    getattr(self,act)['moment'] = {}
                    getattr(self,act)['moment']['candle'],getattr(self,act)['moment']['feature'] = self.split_num_str(string)
                    getattr(self,act)['moment']['mode'] = 'simple'
                    getattr(self,act)['moment']['change'] = 0 
            # print(getattr(self,act)['moment'])

        def split_num_str(self,mess):
            x = np.array(list(mess))
            y = np.array([item.isdigit() for item in x])
            number_part = x[y]
            string_part = x[np.invert(y)]
            if len(string_part) > 1:
                string_part = ''.join(string_part)
            else:
                string_part = str(string_part[0])    
            return (str(number_part[0]),string_part)

            # ope = {
            #     '+' : operator.add,
            #     '-' : operator.sub,
            #     '*' : operator.mul
            # }

    p1 = {
    'path_candle_file' : '../builders/warehouse/candle_data/' + '30min_1529921395_6183-2_0-40432139_bitstamp.csv',
    'path_trendline_file': '../builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
    'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
    'buy' : {'candle':'1','moment':'1rsi*1.03'},
    'sell' : {'candle':'4-6','moment':'1td_s*1.03'},
    'tourist': {
        'version': 'tourist1',
        'mode': 'greater_than_limit',
        'condition_parameter': 'm',
        'limit': 0,
        'limit1': 0,
        'limit2': 0
    },
    'digger': {'version': 'digger1'},
    'sculptor': {'version': 'sculptor3'},
    'researcher': {'version': 'researcher1'}
    }

    event1 = event(p1)

    print(event1.buy)
    print(event1.sell)

if __name__ == '__main__':
    main()         








