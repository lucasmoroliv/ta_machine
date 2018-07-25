import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint

def callable(p):
    data = get_data(p)
    full_trendlines_df = get_full_trendlines_df(data)
    filtered_trendlines_df = conditions1(p,full_trendlines_df)
    goodtimes = fix_array(p,filtered_trendlines_df)
    return goodtimes

# ---------------------------------------------------------------------------------
# * SECTION 1 *
# Each one of the functions in this section must return a filtered_trendlines_df. 

def conditions1(p,full_trendlines_df):
    if p['chart_filter']['mode'] == 'greater_than_limit':
        filtered_trendlines_df = full_trendlines_df[full_trendlines_df[p['chart_filter']['condition_parameter']]>p['chart_filter']['limit']]
    elif p['chart_filter']['mode'] == 'less_than_limit':
        filtered_trendlines_df = full_trendlines_df[full_trendlines_df[p['chart_filter']['condition_parameter']]<p['chart_filter']['limit']]
    elif p['chart_filter']['mode'] == 'greater_than_limit1_less_than_limit2':
        filtered_trendlines_df = full_trendlines_df[(full_trendlines_df[p['chart_filter']['condition_parameter']]>p['chart_filter']['limit1']) & (full_trendlines_df[p['chart_filter']['condition_parameter']]<p['chart_filter']['limit2'])]
    elif p['chart_filter']['mode'] == 'less_than_limit1_greater_than_limit2':
        filtered_trendlines_df = full_trendlines_df[(full_trendlines_df[p['chart_filter']['condition_parameter']]<p['chart_filter']['limit1']) | (full_trendlines_df[p['chart_filter']['condition_parameter']]>p['chart_filter']['limit2'])]
    return filtered_trendlines_df

# ---------------------------------------------------------------------------------
# * SECTION 2 *
# Here is a space to store all sorts of auxiliary functions that will help the pattern
#  funcions to find their filtered_trendlines_df.

def get_full_trendlines_df(data):
    trendlines_df = pd.DataFrame(data['trendlines'])
    goodtimes_df = pd.DataFrame()
    goodtimes_df['ts_start'] = trendlines_df['test0'].apply(lambda x: calendar.timegm(time.strptime(x, '%Y-%m-%d %H:%M:%S')))
    goodtimes_df['m'] = trendlines_df['b']
    goodtimes_df['num_tests'] = trendlines_df['tests']
    goodtimes_df['ts_end'] = get_ts_end(trendlines_df)
    goodtimes_df['num_candles'] = trendlines_df['candles']
    return goodtimes_df

def get_ts_end(trendlines_df):
    ts_end_list = []
    for index, row in trendlines_df.iterrows():
        ts_end = row['test{0}'.format(row['tests']-1)]
        ts_end = calendar.timegm(time.strptime(ts_end, '%Y-%m-%d %H:%M:%S'))
        ts_end_list.append(ts_end)
    return np.array(ts_end_list)

def fix_array(p,filtered_trendlines_df):
    df = get_dataframe(p['path_candle_file'])
    candle_sec = (df['timestamp'][1] - df['timestamp'][0])
    all_list = []
    mess = filtered_trendlines_df[['ts_start','ts_end']].copy().values
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

def get_data(p):
    with open(p['chart_filter']['path_trendline_file']) as f:
        data = json.load(f)
        return filterbydate_data(data,p['timeframe'])

def get_dataframe(df_file):
    return pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])

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
    print('Runtime: ',time2-time1)