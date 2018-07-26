import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint

def main():
    t = {
        'candle_file' : '30min_1529921395_6183-2_0-40432139_bitstamp.csv',
        'timeframe' : ('2018-01-01 00:00:00','2018-06-19 23:30:00'),
        'max_span' : 100,
        'min_span' : 40,
        'upper_limit' : 0.0005,
        'lower_limit' : 0.001,
        'min_tests' :  4,
        'max_tests' : 15,
        'min_inbetween' : None
    }
    t['min_inbetween'] = int(t['min_span']*0.1)
    callable(t)

def callable(t):
    t['trendline_file'] = standard_name(t)
    messed_trendlines_list = get_trendlines(t)
    trendlines_list = shrink_data(messed_trendlines_list)
    trendlines_data = {
        'type': t,
        'trendlines': trendlines_list
    }
    path_trendlines_file = 'warehouse/trendlines/' + t['trendline_file']
    with open(path_trendlines_file, 'w') as outfile:
        json.dump(trendlines_data, outfile)

def shrink_data(messed_trendlines_list):
    full_data_df = pd.DataFrame(messed_trendlines_list)
    blacklisted_names = ['tests','a','b']
    allnames_list = list(full_data_df)
    no_blacklisted_names = [i for i in allnames_list if i not in blacklisted_names]
    data_df = full_data_df[no_blacklisted_names].copy()
    rejected_indexes = []
    data_list = data_df.drop('candles',axis=1).values.tolist()
    for index_set1 in range(data_df.shape[0]-1):
        if index_set1 in rejected_indexes:
            continue
        set1 = set([i for i in data_list[index_set1] if not i is np.nan])
        for index_set2 in range(index_set1+1,data_df.shape[0]):
            set2 = set([i for i in data_list[index_set2] if not i is np.nan])
            inter = len(set1 & set2)
            if inter >= 2:
                span_set1 = data_df['candles'][index_set1]
                span_set2 = data_df['candles'][index_set2]
                if span_set1 >= span_set2:
                    rejected_indexes.append(index_set2)
                else:
                    rejected_indexes.append(index_set1)
                    break
    new_df = full_data_df.drop(rejected_indexes)
    messed_listofdict = new_df.to_dict('records')
    listofdict = take_nan_out(messed_listofdict)
    return listofdict

def take_nan_out(mess):
    for item in mess:
        pop_list = []
        for key in item.keys():
            if pd.isnull(item[key]):
                pop_list.append(key)
        [item.pop(i) for i in pop_list]
    return mess

def get_trendlines(t):
    df = get_dataframe('../warehouse/candle_data/' + t['candle_file'])
    df = filterbydate_df(df,t['timeframe'])
    low_array = df[['timestamp','low']].copy().values
    trendlines_list = []
# It will iterate for every candle within timeframe that can be a trendline with the parameters previously defined. It does not need to loop over all the candles because of min_span.
    for index_point1 in range(low_array.shape[0]-t['min_span']+1):
# We need to decide over the inferior and superior limits that will give us the interval of possible point2 values.
        if (index_point1+t['max_span']) >= (low_array.shape[0]):
            superior_index_point2 = low_array.shape[0]
        else:
            superior_index_point2 = index_point1+t['max_span'] - 1
        inferior_index_point2 = index_point1+t['min_span']-1
# After finding the interval, we use it to make a section in low_array and call it point2_lows, where there are the timestamp and low price of every candle point2 will be.
        point2_lows = low_array[inferior_index_point2:superior_index_point2+1]
# This approach of calculating the equation coeficients was chose becuase of its performance.
        y2 = point2_lows[:,1]
        x2 = point2_lows[:,0]
        x1 = np.full(point2_lows.shape[0],low_array[index_point1,0])
        y1 = np.full(point2_lows.shape[0],low_array[index_point1,1])
        a = (y1 - y2)/(x1 - x2)
        b = y2-x2*(y1-y2)/(x1-x2)
# The arrays a and b represent together all possible equation lines for this given index_point1. Now we test each one of them against our trendlines parameters.
        for equation_index in range(a.shape[0]):
# These next arrays are created in order to calculate the line_values array, and it's siblings lower_line and upper_line.
            ts_values = low_array[index_point1:superior_index_point2+1,0]
            low_values = low_array[index_point1:superior_index_point2+1,1]
            index_array = np.arange(low_values.shape[0])
            a_value = np.full(ts_values.shape[0],a[equation_index])
            b_value = np.full(ts_values.shape[0],b[equation_index])
            line_values = a_value*ts_values+b_value
            lower_line = line_values*(1-t['lower_limit'])
            upper_line = line_values*(1+t['upper_limit'])
            above_lower_limit = low_values>lower_line

            first_false_index = np.where(above_lower_limit == False)[0]
            if len(first_false_index) == 0:
                first_false_index = superior_index_point2+1
            else:
                first_false_index = first_false_index[0]
            possible_tests = index_array[(low_values<upper_line) & (low_values>lower_line)]
            index_test_list = [0]
            if first_false_index >= t['min_span']:
                for cand in possible_tests[1:]:
                    if index_test_list[-1] < (cand-t['min_inbetween']) and cand < first_false_index:
                        index_test_list.append(cand)

                if len(index_test_list) >= t['min_tests'] and len(index_test_list) <= t['max_tests']:
                    response_dict = {
                        'tests': len(index_test_list),
                        'candles': int(index_test_list[-1]+1),
                        'a': float(a[equation_index]),
                        'b': float(b[equation_index]),
                    }
                    for i in range(len(index_test_list)):
                        response_dict['test{0}'.format(i)] = str(datetime.datetime.utcfromtimestamp(ts_values[index_test_list[i]]))
                    trendlines_list.append(response_dict)
    return trendlines_list

def standard_name(t):
    trendline_file = t['candle_file'].split('_')[0] + '_' + str(t['timeframe'][0].split()[0]) + '_' + str(t['timeframe'][1].split()[0]) + \
                '_' + str(t['min_span']) + '_' + str(t['max_span']) + '_' + str(t['min_tests']) + '_' + str(t['max_tests']) + '_' + \
                str(t['upper_limit']).split('.')[1] + '_' + str(t['lower_limit']).split('.')[1] + '_' + str(t['min_inbetween']) + '.txt'
    return trendline_file

def get_dataframe(df_file):
    return pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])

def filterbydate_df(df,timeframe):
    # Input the dataframe and timeframe you want and the function gives you the dataframe filtered by those dates found in the timeframe variable.
    struct_time0 = time.strptime(timeframe[0], '%Y-%m-%d %H:%M:%S')
    struct_time1 = time.strptime(timeframe[1], '%Y-%m-%d %H:%M:%S')
    inferior = calendar.timegm(struct_time0)
    superior = calendar.timegm(struct_time1)
    try:
        df_partition = df[(df.timestamp >= inferior) & (df.timestamp <= superior)]
        df_partition.index = range(len(df_partition.index))
        return df_partition
    except:
        ('\nYou picked a bad timeframe mate.')

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
