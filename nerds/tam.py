import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,sys
sys.path.append('../builders')
import momentum_indicators
from pprint import pprint

class event:

    def __init__(self,p):

        for key,value in p.items():
            setattr(self,key,value)

        self.import_module(p)
        self.candles_df = self.get_dataframe(p['path_candle_file'])
        self.candle_sec = self.candles_df.index[1] - self.candles_df.index[0]
        self.units_list = self.get_units_list(p)
        self.fill_unit_list()  

    def get_units_list(self,p):
        if self.toggle_tourist == True:
            self.goodtimes = self.tourist.callable(p)
            return self.digger.callable(p,self.goodtimes)
        elif self.toggle_tourist == False: 
            return self.digger.callable(p)

    def get_dataframe(self,df_file):
        # This function needs improvement. Though functional, it could be built more elegantly.
        pre_candles_df = pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])
        candles_df = pre_candles_df.set_index('timestamp')
        return candles_df

    def fill_unit_list(self):
        ope = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        'simple': operator.add,
        'absolute': operator.add,
        }
        # Everything here is done for both the 'buy' and 'sell' action, one at a time.
        # The |TASK1| goal is to create 'getattr(self,act)['moment']' dictionary. We will need this dictionary to achieve the next task.
        # The |TASK2| goal is to add relevant information to the 'units_list'.

        for act in ['buy','sell']:

            # |TASK1|
            # It starts with the update of the 'getattr(self,act)['candle']' value. The string will be turned in to a list of strings, contaning every candle we can possible start the buy position. 
            if '-' in getattr(self,act)['candle']:
                interval = getattr(self,act)['candle'].split('-')
                getattr(self,act)['candle'] = list(str(item) for item in range(int(interval[0]),int(interval[1])+1))
            else:
                getattr(self,act)['candle'] = [getattr(self,act)['candle']]
            # The value 'getattr(self,act)['moment']' is store in act_moment so we can then asign an empty dictionary to it, erasing its prior value. 
            act_moment = getattr(self,act)['moment']
            getattr(self,act)['moment'] = {}
            # Finding 'increment_mode' value.
            ope_index = max([act_moment.find(mode) for mode in ['*','+','-']])
            if ope_index > 1:
                getattr(self,act)['moment']['increment_mode'] = act_moment[ope_index]
            else:
                getattr(self,act)['moment']['increment_mode'] = 'none'
            # Finding 'index_mode'.
            if act_moment.isdigit():
                getattr(self,act)['moment']['index_mode'] = 'absolute'
            else:
                getattr(self,act)['moment']['index_mode'] = 'feature'
            # Finding 'candle_mode':
            if len(getattr(self,act)['candle']) == 1:
                getattr(self,act)['moment']['candle_mode'] = 'simple'
            elif len(getattr(self,act)['candle']) >= 2:
                getattr(self,act)['moment']['candle_mode'] = 'interval'
            # There are two different ways to calculate the last tree keys ('candle','value' and 'feature') dependeding on which 'index_mode' value the act has. 
            # Along these two ways, finding 'before_ope' and 'after_ope' will make it easeir to calculate these last keys.    
            if getattr(self,act)['moment']['index_mode'] == 'feature':
                # There are also two ways to find 'before_ope' and 'after_ope'. One way if there is an operator and another if there is none.
                if getattr(self,act)['moment']['increment_mode'] == 'none':
                    before_ope = act_moment
                    after_ope = 'none'
                else:
                    before_ope,after_ope = act_moment.split(act_moment[ope_index])
                # Finding 'candle'.
                getattr(self,act)['moment']['ref_candle'] = int(self.split_num_str(before_ope)[0])
                # Finding 'value'.
                getattr(self,act)['moment']['value'] = after_ope
                # Finding 'feature'. 
                getattr(self,act)['moment']['feature'] = self.split_num_str(before_ope)[1]
            elif getattr(self,act)['moment']['index_mode'] == 'absolute':
                before_ope = act_moment
                # Finding 'candle'.
                getattr(self,act)['moment']['ref_candle'] = 'absolute'
                # Finding 'value'.
                getattr(self,act)['moment']['value'] = before_ope
                # Finding 'feature'.
                getattr(self,act)['moment']['feature'] = 'absolute'

            # |TASK2|
            # First we deal with getattr(self,act)['moment']['index_mode'] == 'feature' and later when its value is 'absolute'.
            for unit in self.units_list:
                # We start by creating these two following variables. These will be used extensively on the next lines therefore is worthwhile make them look smaller, for readability sake.
                act_candle = getattr(self,act)['candle']
                act_moment = getattr(self,act)['moment']
                # The key_name will also make some indexation done easiear and in a more readable way on the next lines.
                if act_moment['increment_mode'] in ['*','+','-']:
                    key_name = act_moment['feature'] + act_moment['increment_mode'] + act_moment['value'] 
                else:
                    key_name = act_moment['feature']
                # We split the creation of unit keys in two parts.
                # In |PART1| we add 'low' and 'high' info to the candles of act_candle.
                # In the |PART2| we add the feature 'act_moment['feature']' to the candle 'act_moment['ref_candle']'.
                # |PART1|
                for candle in act_candle:
                    if not candle in unit.keys():
                        unit[candle] = {}
                    candle_ts = unit['0']['ts'] + int(candle) * self.candle_sec
                    unit[candle]['low'] = self.candles_df.loc[candle_ts]['low']
                    unit[candle]['high'] = self.candles_df.loc[candle_ts]['high']
                # |PART2|
                if not act_moment['ref_candle'] in unit.keys():
                    unit[act_moment['ref_candle']] = {}
                if act_moment['increment_mode'] == 'none':
                    pass
                    unit[act_moment['ref_candle']][act_moment['feature']] = self.candles_df.loc[candle_ts][act_moment['feature']]  
                else:
                    unit[act_moment['ref_candle']][key_name] = ope[act_moment['increment_mode']](self.candles_df.loc[candle_ts][act_moment['feature']],float(act_moment['value']))
                
    def update_df(self,df,name,array):
        serie = pd.Series(array)
        df[name] = array
        return df

    def import_module(self,p):
        self.tourist = __import__(p['tourist']['version'])
        self.digger = __import__(p['digger']['version'])
        self.sculptor = __import__(p['sculptor']['version'])
        self.researcher = __import__(p['researcher']['version'])

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
    'buy' : {'candle':'1','moment':'2high'},
    'sell' : {'candle':'4-6','moment':'3open'},
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
pprint(event1.units_list)
