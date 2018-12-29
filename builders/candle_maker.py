import pandas as pd
import numpy as np
import csv,time,datetime,calendar,math
from pprint import pprint

def main():
    m = 60
    h = 60*m
    d = 24*h
    w = 7*d
    c = {
        'candle_str': '12h',
        'candle_sec': 12*h,
        'data_path': 'warehouse/historical_data/bitstampUSD.csv',
        'ts_reference': 1315785600
    }
    csv_array = get_array(c)
    make_filename_main(c,csv_array)
    get_start_ts(c,csv_array)
    make_csv(c,csv_array)

def callable(c):
    csv_array = get_array(c)
    get_start_ts(c,csv_array)
    return make_list(c,csv_array)

def make_filename_main(c,csv_array):
    c['output_path'] = 'warehouse/candle_data/' + c['candle_str'] + '_bitstamp.csv' 

def make_list(c,csv_array):
    price_open = 0
    price_high = 0
    price_low = 0
    price_close = 0
    change = 0
    checker = 0
    volume = 0
    candle_index = 0
    first_ts = next_item(csv_array[:,0],c['start_ts'])
    index_first_ts = np.where(csv_array[:,0] == first_ts)[0][0]
    candles_list = []

    for row in csv_array[index_first_ts:]:
        if checker == 1:
            if row[0] < (c['start_ts'] + (candle_index + 1) * c['candle_sec']):
                volume = volume + row[2]
                price_close = row[1]
                if row[1] > price_high:
                    price_high = row[1]
                    continue
                if row[1] < price_low:
                    price_low = row[1]
            else:
                change = ( price_close - price_open ) / price_open
                checker = 0
                candles_list.append([str(datetime.datetime.utcfromtimestamp(c['start_ts']+c['candle_sec']*candle_index)),c['start_ts']+c['candle_sec']*candle_index,price_open,price_high,price_low,price_close,volume,change])
                candle_index = candle_index + 1
                volume = 0

        if checker == 0:
            while row[0] > (c['start_ts'] + (candle_index + 1) * c['candle_sec']):
                candles_list.append([str(datetime.datetime.utcfromtimestamp(c['start_ts']+c['candle_sec']*candle_index)),c['start_ts']+c['candle_sec']*candle_index,price_open,price_high,price_low,price_close,volume,change])
                
                candle_index = candle_index + 1

            price_open = row[1]
            price_high = price_open
            price_low = price_open
            price_close = price_open
            volume = volume + row[2]
            checker = 1

    return candles_list

def make_csv(c,csv_array):
    price_open = 0
    price_high = 0
    price_low = 0
    price_close = 0
    change = 0
    checker = 0
    volume = 0
    candle_index = 0
    first_ts = next_item(csv_array[:,0],c['start_ts'])
    index_first_ts = np.where(csv_array[:,0] == first_ts)[0][0]

    with open(c['output_path'], 'w', newline='') as file:
        spamwriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for row in csv_array[index_first_ts:]:
            if checker == 1:
                if row[0] < (c['start_ts'] + (candle_index + 1) * c['candle_sec']):
                    volume = volume + row[2]
                    price_close = row[1]
                    if row[1] > price_high:
                        price_high = row[1]
                        continue
                    if row[1] < price_low:
                        price_low = row[1]
                else:
                    change = ( price_close - price_open ) / price_open
                    checker = 0
                    spamwriter.writerow([str(datetime.datetime.utcfromtimestamp(c['start_ts']+c['candle_sec']*candle_index)),c['start_ts']+c['candle_sec']*candle_index,price_open,price_high,price_low,price_close,volume,change])
                    candle_index = candle_index + 1
                    volume = 0

            if checker == 0:
                while row[0] > (c['start_ts'] + (candle_index + 1) * c['candle_sec']):
                    spamwriter.writerow([str(datetime.datetime.utcfromtimestamp(c['start_ts']+c['candle_sec']*candle_index)),c['start_ts']+c['candle_sec']*candle_index,price_open,price_high,price_low,price_close,volume,change])
                    candle_index = candle_index + 1

                price_open = row[1]
                price_high = price_open
                price_low = price_open
                price_close = price_open
                volume = volume + row[2]
                checker = 1

def next_item(array,ts):
    return array[array>=ts][0]

def get_start_ts(c,csv_array):
    first_ts_array = csv_array[0,0]
    c['start_ts'] = math.ceil( ( first_ts_array - c['ts_reference'] ) / c['candle_sec'] ) * c['candle_sec'] + c['ts_reference']

def get_array(c):
    csv_array = pd.read_csv(c['data_path'], names=['timestamp','price','volume']).values
    return csv_array

if __name__ == '__main__':
    x1 = time.time()
    main()
    x2 = time.time()
    print('Run time: ',x2-x1)
