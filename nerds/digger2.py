import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import tourist1k

def callable(goodtimes):
    candles0_array = pattern1(goodtimes)
    return candles0_array

def pattern1(goodtimes):
    candles0_array = goodtimes[:,0]
    return candles0_array
