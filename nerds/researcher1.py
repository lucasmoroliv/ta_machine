import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt

def callable(p,info_list):
    data = output(p,info_list)
    return data

def output(p,info_list):
    data = {
        'sample': {
            'lowest_candle': func1(p,info_list,'frombuytothislow')[0],
            'lowest_amp': func1(p,info_list,'frombuytothislow')[1],
            'highest_candle': func1(p,info_list,'frombuytothishigh')[0],
            'highest_amp': func1(p,info_list,'frombuytothishigh')[1],
            },
        'event': {},
        'parameters': p
    }
    success_array = [data['sample']['highest_amp']>p['target']]
    # pprint(success_array)
    # pprint(data['sample']['highest_candle'].shape)
    # pprint(data['sample']['highest_candle'][success_array].shape)
    data['event']['lowest_candle'] = data['sample']['lowest_candle'][success_array]
    data['event']['lowest_amp'] = data['sample']['lowest_amp'][success_array]
    data['event']['highest_candle'] = data['sample']['highest_candle'][success_array]
    data['event']['highest_amp'] = data['sample']['highest_amp'][success_array]
    return data

def func2(p,array,):
# It gets the highest_candle_array from func1 and finds the boolean array of it
# where the true values are the ones greater than the target, defined in the
# parameters dictionary. The boolean array will then filter any array passed by
# this function.
    return array[array>p['target']]

def func1(p,info_list,mode):
# It can receive two mode values, 'frombuytothislow' and 'frombuytothishigh'. If
# former is the case, it will be returned a tuple of two arrays, the first
# being a character representing the lowest candle of each unit, and the second
# being it's respectice change comparing to the buy price. The latter mode case
# will do the same thing but for the highest candle of each unit.
    mode_intrade = get_mode_intrade(p,info_list,mode)
    mode_candle_list = []
    mode_amp_list = []
    if mode == 'frombuytothislow':
        for unit in mode_intrade:
            mode_candle_list.append(min(unit, key=unit.get))
            mode_amp_list.append(unit[mode_candle_list[-1]])
    elif mode == 'frombuytothishigh':
        for unit in mode_intrade:
            mode_candle_list.append(max(unit, key=unit.get))
            mode_amp_list.append(unit[mode_candle_list[-1]])
    return np.array(mode_candle_list),np.array(mode_amp_list)

def get_mode_intrade(p,info_list,mode):
# It can receive any key present at info_list as a mode. The function returns
# the unit by unit, candle by candle, the mode and its value.
    sample_list = []
    for unit in info_list:
        unit_dict = {}
        for key in range(p['buy']['candle'],p['sell']['candle']+1):
            unit_dict[key] = unit[key][mode]
        sample_list.append(unit_dict)
    sample_array = np.array(sample_list)
    return sample_array

# def get_bool_success(p,dict_arrays):
#     profit_array = get_profit_array(p,dict_arrays)
#     bool_array = [profit_array>p['target']]
#     return bool_array
#
# def get_profit_array(p,dict_arrays):
#     profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
#     return profit_array
#
#
# def success_low_stats(p,dict_arrays):
#     profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
#     success_array = [profit_array>p['target']]
#     return success_rate
#
# def get_success_array(p,dict_arrays):
#     profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
#     success_array = profit_array[profit_array>p['target']]
#     return success_array
#
# def get_success_rate(p,dict_arrays):
#     profit_array = ( dict_arrays['candle_{0}_{1}'.format(p['sell']['candle'],p['sell']['moment'])] - dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])] ) / dict_arrays['candle_{0}_{1}'.format(p['buy']['candle'],p['buy']['moment'])]
#     success_amt = profit_array[profit_array>p['target']].shape[0]
#     sample_amt = profit_array.shape[0]
#     success_rate = success_amt/sample_amt
#     return success_rate

# def get_profit_array(dict_arrays,buy,end_candle):
#     dict_profits = {}
#     price_buy = dict_arrays['candle_{0}_{1}'.format(buy['candle'],buy['moment'])]
#     for candle in range(buy['candle']+1,end_candle+1):
#         dict_profits['o{0}_h{1}'.format(buy['candle'],candle)] = ( dict_arrays['candle_{0}_{1}'.format(candle,'high')] - price_buy ) / price_buy
#     return dict_profits

def arraify(info_list):
    dict_lists = {}
    for candle in info_list[0]:
        for info in info_list[0][candle]:
            dict_lists['candle_{0}_{1}'.format(candle,info)] = []
    for graph in info_list:
        for candle in graph:
            for info in graph[candle]:
                dict_lists['candle_{0}_{1}'.format(candle,info)].append(graph[candle][info])
    dict_arrays = {}
    for key in list(dict_lists):
        dict_arrays[key] = np.array(dict_lists[key])
    return dict_arrays

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
