import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,sys
sys.path.append('../builders')
import momentum_indicators
from pprint import pprint

def main():

    class event:

        def __init__(self,p):

            for key,value in p.items():
                setattr(self,key,value)

            self.import_module(p)
            self.standard_filter()
            self.candles_df = self.get_dataframe(p['path_candle_file'])
            self.features_list = [self.buy['moment']['feature'],self.sell['moment']['feature']]
            self.candle_sec = self.candles_df.index[1] - self.candles_df.index[0]
            if self.toggle_tourist == True:
                self.goodtimes = self.tourist.callable(p)
                units_list = self.digger.callable(p,self.goodtimes)
            elif self.toggle_tourist == False: 
                units_list = self.digger.callable(p)
            self.fill_unit_list(units_list)  
            pprint(units_list)

        def get_dataframe(self,df_file):
            # This function needs improvement. Though functional, it could be built more elegantly.
            pre_candles_df = pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])
            pre_candles_df = pre_candles_df.set_index('timestamp')
            rsi = momentum_indicators.rsi(self.path_candle_file)
            candles_df = self.update_df(pre_candles_df,'rsi',rsi[:,1])
            return candles_df

        def fill_unit_list(self,units_list): 
            ope = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            'simple': operator.add,
            'absolute': operator.add,
            }
            for act in ['buy','sell']:
                buy_moment = getattr(self,act)['moment']
                # The following statement splits the section in two. Firstly we handle every mode but 'absolute', and secondly we deal with only that. At first look it seems to be a good decision.
                if buy_moment['mode'] in ['*','+','-']:
                    key_name = buy_moment['feature'] + buy_moment['mode'] + getattr(self,act)['moment']['value'] 
                else:
                    key_name = buy_moment['feature']
                if not buy_moment['mode'] == 'absolute':
                    for unit in units_list:
                        # We start by dealing with the single candles. Intervals are handled later.
                        if not '-' in getattr(self,act)['candle']:
                            if not buy_moment['candle'] in unit.keys():
                                unit[buy_moment['candle']] = {}
                            candle_ts = unit['0']['ts'] + int(buy_moment['candle']) * self.candle_sec
                            if not buy_moment['feature'] in ['open','high','low','close']:
                                unit[buy_moment['candle']][buy_moment['feature']] = self.candles_df.loc[candle_ts][buy_moment['feature']]  
                                if buy_moment['mode'] in ['*','+','-']:
                                    unit[buy_moment['candle']]['close{0}{1}'.format(buy_moment['mode'],getattr(self,act)['moment']['value'] )] = ope[buy_moment['mode']](self.candles_df.loc[candle_ts]['close'],float(buy_moment['value'])) 
                                else:
                                    unit[buy_moment['candle']]['close'] = ope[buy_moment['mode']](self.candles_df.loc[candle_ts]['close'],float(buy_moment['value'])) 
                            else:
                                unit[buy_moment['candle']][key_name] = ope[buy_moment['mode']](self.candles_df.loc[candle_ts][buy_moment['feature']],float(buy_moment['value'])) 
                        else:                   
                            pass       
                # Now the second part where we deal with the 'absolute' mode. 
                # else:
                #     for unit in units_list:
                #         if not '-' in getattr(self,act)['candle']:
                #                 unit[buy_moment['candle']] = {}


        def update_df(self,df,name,array):
            serie = pd.Series(array)
            df[name] = array
            return df

        def import_module(self,p):
            self.tourist = __import__(p['tourist']['version'])
            self.digger = __import__(p['digger']['version'])
            self.sculptor = __import__(p['sculptor']['version'])
            self.researcher = __import__(p['researcher']['version'])

        def standard_filter(self):
            for act in ['buy','sell']:
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
                elif getattr(self,act)['moment'].isdigit():
                    value = float(getattr(self,act)['moment'])
                    getattr(self,act)['moment'] = {}
                    getattr(self,act)['moment']['value'] = value
                    getattr(self,act)['moment']['mode'] = 'absolute'
                    getattr(self,act)['moment']['candle'] = 'any'
                    getattr(self,act)['moment']['feature'] = 'any'
                # '1h','2rsi','4c'  
                elif ope_index == -1 and sum(char.isalpha() for char in getattr(self,act)['moment']) >= 1:
                    string = getattr(self,act)['moment']
                    getattr(self,act)['moment'] = {}
                    getattr(self,act)['moment']['candle'],getattr(self,act)['moment']['feature'] = self.split_num_str(string)
                    getattr(self,act)['moment']['mode'] = 'simple'
                    getattr(self,act)['moment']['value'] = 0 

        def split_num_str(self,mess):
            mess = np.array(list(mess))
            number_part = mess[np.array([item.isdigit() for item in mess])]
            string_part = mess[np.array([item.isalpha() for item in mess])]
            if len(string_part) > 1:
                string_part = ''.join(string_part)
            else:
                string_part = str(string_part[0])    
            if len(number_part) > 1:
                number_part = ''.join(number_part)
            else:
                number_part = str(number_part[0])    
            return (number_part,string_part)



    p1 = {
    'path_candle_file' : '../builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'timeframe' : ['2014-01-04 00:00:00','2018-04-19 00:00:00'],
    'buy' : {'candle':'1','moment':'1open*1.01'},
    'sell' : {'candle':'1','moment':'1rsi*1.10'},
    'toggle_tourist': True,
    'tourist': {
        'version': 'tourist1',
        'path_trendline_file': '../builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_200_4_15_0015_001_4.txt',
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

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)







