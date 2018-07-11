import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint

def callable(p):
    big_array = get_and_organize_data(p)
    goodtimes = conditions1(big_array)
    candles0_array = pattern1(goodtimes)
    return candles0_array

def get_and_organize_data(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open('../warehouse/td_data/td_setup_30min_bitstamp.csv', newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        list = []
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        big_array = np.array(big_list)
        big_array.astype(int)
    return big_array

def conditions1(big_array):
    # For td_setup : equal to 9 for "normal" td_sell_setup, 80 for minimal_sell_setup or 90 for perfect_sell_setup
    #              : equal to -9 for "normal" td_buy_setup, -80 for minimal_buy_setup or -90 for perfect_sell_setup
    # For td_countdown : equal to 13 for td_sell_countdown
    #                  : equal to -13 for td_buy_countdown
    small_array = big_array[big_array[:,1]==9]
    return small_array

def pattern1(goodtimes):
    candles0_array = goodtimes[:,0]
    return candles0_array

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
