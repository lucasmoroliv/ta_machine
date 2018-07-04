import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint

def callable(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, min_inbetween):
    data = get_trendlines(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, min_inbetween)

def main():
    max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween = parameters()
    object_file = standardize_name(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween)
    messed_trendlines_list = get_trendlines(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween)
    trendlines_list = shrink_data(messed_trendlines_list)
    data = { 'type': {'df_file': df_file,
                      'timeframe': timeframe,
                      'max_span': max_span,
                      'min_span': min_span,
                      'upper_limit': upper_limit,
                      'lower_limit': lower_limit,
                      'min_tests': min_tests,
                      'max_tests': max_tests,
                      'min_inbetween': min_inbetween},
                      'trendlines': trendlines_list
    }
    path_data_object = '../warehouse/trendlines/' + object_file
    with open(path_data_object, 'w') as outfile:
        json.dump(data, outfile)

def parameters():
    df_file = '30min_1529921395_6183-2_0-40432139_bitstamp.csv'
    timeframe = ('2014-01-01 00:00:00','2018-06-19 23:30:00')
    max_span = 500
    min_span = 80
    upper_limit = 0.0005
    lower_limit = 0.001
    min_tests = 3
    max_tests = 15
    min_inbetween = int(min_span*0.1)
    return max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween

def standardize_name(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween):
    file_name = df_file.split('_')[0] + '_' + str(timeframe[0].split()[0]) + '_' + str(timeframe[1].split()[0]) + \
                '_' + str(min_span) + '_' + str(max_span) + '_' + str(min_tests) + '_' + str(max_tests) + '_' + \
                str(upper_limit).split('.')[1] + '_' + str(lower_limit).split('.')[1] + '_' + str(min_inbetween) + '.txt'
    return file_name

def shrink_data(messed_data):
    full_data_df = pd.DataFrame(messed_data)
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

def get_trendlines(max_span, min_span, df_file, timeframe, upper_limit, lower_limit, min_tests, max_tests, min_inbetween):
    df = get_dataframe('../warehouse/candle_data/' + df_file)
    df = filterbydate_df(df,timeframe)
    low_array = df[['timestamp','low']].copy().values
    trendlines_list = []
# It will iterate for every candle within timeframe that can be a trendline with the parameters previously defined. It does not need to loop over all the candles because of min_span.
    for index_point1 in range(low_array.shape[0]-min_span+1):
# We need to decide over the inferior and superior limits that will give us the interval of possible point2 values.
        if (index_point1+max_span) >= (low_array.shape[0]):
            superior_index_point2 = low_array.shape[0]
        else:
            superior_index_point2 = index_point1+max_span - 1
        inferior_index_point2 = index_point1+min_span-1
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
            lower_line = line_values*(1-lower_limit)
            upper_line = line_values*(1+upper_limit)
            above_lower_limit = low_values>lower_line

            first_false_index = np.where(above_lower_limit == False)[0]
            if len(first_false_index) == 0:
                first_false_index = superior_index_point2+1
            else:
                first_false_index = first_false_index[0]
            possible_tests = index_array[(low_values<upper_line) & (low_values>lower_line)]
            index_test_list = [0]
            if first_false_index >= min_span:
                for cand in possible_tests[1:]:
                    if index_test_list[-1] < (cand-min_inbetween) and cand < first_false_index:
                        index_test_list.append(cand)

                if len(index_test_list) >= min_tests and len(index_test_list) <= max_tests:
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

def get_dataframe(df_file):
    return pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])

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
