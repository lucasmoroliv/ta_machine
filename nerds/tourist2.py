import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint


def callable(p):
    big_array = get_and_organize_data(p)
    goodtimes = conditions1(big_array)
    return goodtimes

def get_and_organize_data(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open(p['path_td_file'], newline='') as csvfile:
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
    small_array = big_array[big_array[:,1]==9]
    return small_array

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)