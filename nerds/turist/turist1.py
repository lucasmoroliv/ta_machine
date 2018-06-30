import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint

def main():
    object_file = '../warehouse/trendlines/' + '30min_2017-05-01_2018-04-19_40_100_4_9_0015_001_8.txt'
    timeframe = ['2017-05-10 00:00:00','2018-04-18 00:00:00']
    goodtimes = callable(object_file,timeframe)
    print(goodtimes)

def callable(object_file,timeframe):
    data = get_data(object_file,timeframe)
    df_file = data['type']['file']
    big_array = goodtimes_parameters(data)
    small_array = conditions1(big_array)
    goodtimes = fix_array(small_array,df_file)
    return goodtimes

def conditions1(big_array):
    small_array = big_array[big_array[:,2]>0]
    return small_array

def fix_array(mess,df_file):
    df = get_dataframe(df_file)
    candle_sec = (df['timestamp'][1] - df['timestamp'][0])
    all_list = []
    for index in range(mess.shape[0]):
        x = list(range(int(mess[index,0]),int(mess[index,1])+1,candle_sec))
        for i in x:
            all_list.append(i)
    all_unique = np.array(sorted(set(all_list)))
    checker = 0
    intervals = []
    for i in range(all_unique.shape[0]-1):
        if (i == all_unique.shape[0]-2):
            end = all_unique[i+1]
            intervals.append((start,end))
            break
        if checker == 0:
            start = all_unique[i]
            checker = 1
        if (all_unique[i] + candle_sec != all_unique[i+1]):
            end = all_unique[i]
            intervals.append((start,end))
            start = all_unique[i+1]
    return np.array(intervals)

def get_data(object_file,timeframe):
    with open(object_file) as f:
        data = json.load(f)
        # return filterbydate_data(data,timeframe)
        return data

def goodtimes_parameters(data):
# Here we build an huge array, where each row represent a trendline of the data object, and each column is a parameter of them, like number of tests,
# it's angular coeficient, number of candles, ect. The function therefore receives the data object and returns this big array.
    df = pd.DataFrame(data['trendlines'])
    big_list = []
    for index, row in df.iterrows():
        # --------------------------------------------------------------
        # 0. Start of trendine, expressed in timestamp.
        ts_start = row['test0']
        ts_start = calendar.timegm(time.strptime(ts_start, '%Y-%m-%d %H:%M:%S'))
        # --------------------------------------------------------------
        # 3. Number of price tests on the trendline.
        num_tests = row['tests']
        # --------------------------------------------------------------
        # 1. End of trendline, expressed in timestamp.
        ts_end = row['test{0}'.format(num_tests-1)]
        ts_end = calendar.timegm(time.strptime(ts_end, '%Y-%m-%d %H:%M:%S'))
        # --------------------------------------------------------------
        # 2. Angular coeficient of the trendline, sometimes represented with the letter 'm'.
        m = row['a']
        # --------------------------------------------------------------
        # 4. Number of candles in which the trendline was respected.
        num_candles = row['candles']
        # --------------------------------------------------------------
        # 5. The standard deviation of the difference in seconds of each tests of the trendline.
        tests_list = []
        diff_list = []
        for i in range(num_tests):
            tests_list.append(calendar.timegm(time.strptime(row['test{0}'.format(i)],'%Y-%m-%d %H:%M:%S')))
        for j in range(num_tests-1):
            diff_list.append(tests_list[j+1] - tests_list[j])
        std_diff_tests = np.std(diff_list)
        # --------------------------------------------------------------
        # Now we need to append the list containing every caracteristic of the current trendline to the 'big_list', where all caracacteristics
        # of all trendlines will be stored and once the loop is over 'big_list' will be returned as an array.
        big_list.append([ts_start,ts_end,m,num_tests,num_candles,std_diff_tests])
    # return big_list
    return np.array(big_list)

def get_dataframe(file):
    return pd.read_csv(file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])

def filterbydate_data(data,timeframe):
# The motivation for making the function came from allowing the use of data objects previously created. Now we can create a data
# object with a huge timeframe using trendline5.py and dumping it as a json file. This function will get this huge data object
# and extract only the part defined by the timeframe variable.
    struct_time0 = time.strptime(timeframe[0], '%Y-%m-%d %H:%M:%S')
    struct_time1 = time.strptime(timeframe[1], '%Y-%m-%d %H:%M:%S')
    inferior = calendar.timegm(struct_time0)
    superior = calendar.timegm(struct_time1)
    mb_start = []
    mb_end = []
    for item in data['trendlines']:
        mb_start.append(calendar.timegm(time.strptime(item['test0'],'%Y-%m-%d %H:%M:%S')))
        mb_end.append(calendar.timegm(time.strptime(item['test{0}'.format(len(item)-5)],'%Y-%m-%d %H:%M:%S')))
    mb_start = np.array(mb_start)
    mb_end = np.array(mb_end)
    item_start = int(np.where(mb_start == int(mb_start[mb_start>=inferior][0]))[0][0])
    item_end = int(np.where(mb_end == int(mb_end[mb_end<superior][-1]))[0][0])
    new_type = data['type']
    new_type['timeframe'] = timeframe
    return {'trendlines': data['trendlines'][item_start:item_end+1], 'type': new_type}

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
