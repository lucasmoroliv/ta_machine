import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,importlib,operator,numbers
from pprint import pprint

class event:

    def __init__(self,p):
        for key,value in p.items():
            setattr(self,key,value)

        if '-' in self.buy['candle']:
            self.buy['candle'] = self.buy['candle'].split('-')
        if '-' in self.sell['candle']:
            self.sell['candle'] = self.sell['candle'].split('-')

        # '1h*1.05','2rsi*1.04','4c-500'.
        for mode in ['*','+','-']:
            if mode in self.buy['moment']:
                part1,part2 = self.buy['moment'].split(mode)            
                self.buy['moment'] = {}
                self.buy['moment']['mode'] = mode
                self.buy['moment']['candle'],self.buy['moment']['feature'] = self.split_num_str(str(part1))
        # '5000','3500','2000'. Yet to think about this one. Letting it here for further investigation.
        if isinstance(self.buy['moment'], numbers.Number):
            self.buy['moment'] = {}
            self.buy['moment']['mode'] = 'absolute'
            self.buy['moment']['candle'] = 'any'
            self.buy['moment']['feature'] = 'any'
        # '1h','2rsi','4c'  
        if sum(char.isdigit() for char in self.buy['moment']) == 1:
            string = self.buy['moment']
            self.buy['moment'] = {}
            self.buy['moment']['candle'],self.buy['moment']['feature'] = self.split_num_str(string)
            self.buy['moment']['mode'] = 'simple'
            
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







