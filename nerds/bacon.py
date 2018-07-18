import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,numbers
from pprint import pprint

class event:

    def __init__(self,p):
        for key,value in p.items():
            setattr(self,key,value)

        for act in ['sell','buy']:
            if '-' in getattr(self,act)['candle']:
                getattr(self,act)['candle'] = getattr(self,act)['candle'].split('-')

            # '1h*1.05','2rsi*1.04','4c-500'.
            for mode in ['*','+','-']:
                if mode in getattr(self,act)['moment']: # self.buy['moment']
                    part1,part2 = getattr(self,act)['moment'].split(mode) # self.buy['moment']            
                    getattr(self,act)['moment'] = {} # self.buy['moment']
                    getattr(self,act)['moment']['mode'] = mode # self.buy['moment']['mode']
                    getattr(self,act)['moment']['candle'],getattr(self,act)['moment']['feature'] = self.split_num_str(str(part1))
                    getattr(self,act)['moment']['change'] = part2 
            # '5000','3500','2000'. Yet to think about this one. Letting it here for further investigation.
            if isinstance(getattr(self,act)['moment'], numbers.Number):
                getattr(self,act)['moment'] = {}
                getattr(self,act)['moment']['mode'] = 'absolute'
                getattr(self,act)['moment']['candle'] = 'any'
                getattr(self,act)['moment']['feature'] = 'any'
            # '1h','2rsi','4c'  
            if sum(char.isdigit() for char in getattr(self,act)['moment']) == 1:
                string = getattr(self,act)['moment']
                getattr(self,act)['moment'] = {}
                getattr(self,act)['moment']['candle'],getattr(self,act)['moment']['feature'] = self.split_num_str(string)
                getattr(self,act)['moment']['mode'] = 'simple'
            
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







