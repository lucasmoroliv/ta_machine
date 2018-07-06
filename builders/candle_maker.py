import pandas as pd
import numpy as np
import csv, time, datetime, calendar

def automate():
    minute = 60
    hour = 60*minute
    day = 24*hour
    candle_str_sec = [('1min',minute),
                      ('5min',5*minute),
                      ('30min',30*minute),
                      ('1h',hour),
                      ('2h',2*hour),
                      ('4h',4*hour),
                      ('6h',6*hour),
                      ('12h',12*hour),
                      ('1d',day),
                      ('2d',2*day),
                      ('3d',3*day),
                      ('4d',4*day),
                      ('1w',7*day)]
    for chart in candle_str_sec:
        callable(chart)

def callable(candle_str_sec):
    candle_str = candle_str_sec[0]
    candle_sec = candle_str_sec[1]
    data_file = '../warehouse/historical_data/.bitstampUSD.csv'
    df = get_dataframe(data_file)
    last_timestamp = str(df['timestamp'][df.shape[0]-1])
    last_price_dotted = str(df['price'][df.shape[0]-1])
    last_price = last_price_dotted.replace('.','-')
    last_volume_dotted = str(df['volume'][df.shape[0]-1])
    last_volume = last_volume_dotted.replace('.','-')
    candle_file = '../warehouse/candle_data/' + candle_str + '_' + last_timestamp + '_' + last_price + '_' + last_volume + '_bitstamp.csv'
    timestamp_startofthemonth = find_startofthemonth(df,data_file, candle_sec)
    filter_df(df,candle_file,timestamp_startofthemonth, candle_sec)

def get_dataframe(data_file):
    df = pd.read_csv(data_file, names=['timestamp','price','volume'])
    return df

def find_startofthemonth(df,data_file, candle_sec):
    timestamp_firstcandle = int(df['timestamp'][0])
    fulldate_firstcandle = str(datetime.datetime.utcfromtimestamp(timestamp_firstcandle))
    date_startofthemonth = fulldate_firstcandle.split(' ')[0][:-2] + '01'
    spliting = date_startofthemonth.split('-')
    dt = datetime.datetime(int(spliting[0]), int(spliting[1]), int(spliting[2]), 0, 0, 0, 0)
    timestamp_startofthemonth = calendar.timegm(dt.utctimetuple())
    return timestamp_startofthemonth

def filter_df(df,candle_file,timestamp_startofthemonth, candle_sec):
    candle_number = 1
    price_open = 0
    price_high = 0
    price_close = 0
    price_low = 0
    volume_sum = 0
    checker = 0
    candle_start = timestamp_startofthemonth

    with open(candle_file, 'w', newline='') as file:
        spamwriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in df.values:
# This statement looks for the right "candle_start" variable, which will be the timestamp of the first full candle.
            if checker == 0:
                candle_start = candle_start + candle_sec
                if candle_start > float(row[0]):
                    checker = 1
            if ( checker == 1 ) and ( int(row[0]) > candle_start ):
                price_open = float(row[1])
                price_low = price_open
                price_high = price_open
                checker = 2
            if checker == 2:
                if int(row[0]) < ( candle_start + candle_number * candle_sec ):
                    if float(row[1]) > price_high:
                        price_high = float(row[1])
                    if float(row[1]) < price_low:
                        price_low = float(row[1])
                    volume_sum = volume_sum + float(row[2])
                    price_close = float(row[1])
                else:
                    change = (price_close - price_open)/price_open
                    amplitude = (price_high - price_low)/price_low
                    spamwriter.writerow([datetime.datetime.utcfromtimestamp(candle_start + (candle_number-1) * candle_sec),(candle_start + (candle_number-1) * candle_sec),price_open,price_high, price_close, price_low, volume_sum, change, amplitude])
                    volume_sum = 0
                    price_open = float(row[1])
                    price_low = price_open
                    price_high = price_open
                    candle_number = candle_number + 1

                    if float(row[1]) > price_high:
                        price_high = float(row[1])
                    if float(row[1]) < price_low:
                        price_low = float(row[1])
                    volume_sum = volume_sum + float(row[2])
                    price_close = float(row[1])

if __name__ == '__main__':
    x1 = time.time()
    automate()
    x2 = time.time()
    print('Run time: ',x2-x1)
