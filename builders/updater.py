import pandas as pd
import numpy as np
import csv,time,datetime,calendar,candle_maker,os
from pprint import pprint

def main():
    
    m = 60
    h = 60*m
    d = 24*h
    w = 7*d
    c = {
        'candle_str': '5min',
        'candle_sec': 5*m,
        'data_path': 'egg.csv',
        'ts_reference': 1315785600
    }

    attachment_list = candle_maker.callable(c)
    # append_candles(c,attachement_list)

def append_candles(c,attachement_list):
    csv_path = figureout_csv(c)
    ts_end_history = list(get_dataframe(csv_path).values[-1])[1] 
    start_attachment = attachement_list[0][1]
    print(ts_end_history)
    print(start_attachment)

def figureout_csv(c):
    files_list = os.listdir("warehouse/candle_data")
    for file in files_list:
        if c['candle_str'] in file:
            csv_file = file
    csv_path = "warehouse/candle_data/" + csv_file
    return csv_path 

def get_dataframe(df_file):
    return pd.read_csv(df_file, header=None, names=['timestamp','price','volume'])

if __name__ == '__main__':
    main()




