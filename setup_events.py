# Insert a case_id and triplet as input.
# The program will generate a graph showing candle_0 on a timeline, with each of them
# in a color representing the event the unit is assigned to with the chosen triplet.

import time,datetime,sqlalchemy
import numpy as np
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None
from collections import OrderedDict

def main():

    # Input section
    # -----------------------------------
    case_id = 100
    triplet = (0.055,-0.138,-0.002) # (buy_stop,stop,target)
    # -----------------------------------

    p = get_parameters(case_id)
    units_list = get_units_list(p)  
    raw_df = get_raw(p)

    # The following is a list of two items lists, the first being the "0_ts" of the 
    # unit and the second the unit's event.  
    candle0_event_list = func(triplet,p,raw_df,units_list)

    # Drawing section.
    _, ax = plt.subplots()
    plot_units(ax,candle0_event_list)
    plot_price(ax)
    plt.show()

def plot_price(ax):
    candle_file = "builders/warehouse/candle_data/1h_bitstamp.csv"
    df = get_dataframe(candle_file)
    timestamp_column = df.index.values
    close_column = df.close.values

    ax.plot(timestamp_column,close_column,color="black",linewidth=1)
    plt.yscale('log')

def plot_units(ax,candle0_event_list):
    eventColor = {
        'TW': "b",
        'TC': "g",
        'TL': "r",
        'TP': "c",
        'TN': "y",
        'FW': "b",
        'FC': "g",
        'FL': "r",
        'FP': "c",
        'FN': "y"
    }
    eventLine = {
        'TW': ":",
        'TC': ":",
        'TL': ":",
        'TP': ":",
        'TN': ":",
        'FW': "-",
        'FC': "-",
        'FL': "-",
        'FP': "-",
        'FN': "-"
    }

    for pair in candle0_event_list:
        plt.axvline(x=pair[0], label=pair[1], c=eventColor[pair[1]],linestyle=eventLine[pair[1]],linewidth=1)
        # ax.scatter(pair[0], 1, c=eventColor[pair[1]], label=pair[1], alpha=0.3, edgecolors='none', marker=eventMarker[pair[1]])

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

def func(triplet,p,raw_df,units_list):
    target = triplet[0]
    stop = triplet[1]
    buy_stop = triplet[2]
    candle,moment = translate_order('buy',p['buy'])
    
    target = round(target,3)
    stop = round(stop,3)
    buy_stop = round(buy_stop,3)

    candle0_event_list = []
    for unit in units_list:

        target_price = unit['buy_price']*(1+target)
        stop_price = unit['buy_price']*(1+stop)
        buy_stop_price = unit["buy_price"]*(1+buy_stop)

        if not "operator" in moment or float(moment["change"]) >= 1:
            if unit["buy_farthest_price"] <= buy_stop_price:
                whether_stopped = 'T' # stopped
            else: 
                whether_stopped = 'F' # not-stopped
        elif float(moment["change"]) < 1:
            if unit["buy_farthest_price"] >= buy_stop_price:
                whether_stopped = 'T' # stopped
            else: 
                whether_stopped = 'F' # not-stopped

        if unit['buy_type'] == 'all-bought':
            if unit["sell_realhighest_price"] >= target_price and unit["lowest_price"] > stop_price:
                partition = 'W' # winner
            elif unit["sell_realhighest_price"] < target_price and unit["lowest_price"] > stop_price:
                partition = 'C' # consolidation
            elif unit["sell_realhighest_price"] < target_price and unit["lowest_price"] <= stop_price:
                partition = 'L' # loser
            elif unit["sell_realhighest_price"] >= target_price and unit["lowest_price"] <= stop_price:
                start_index = unit['buy_last_executed_index'] + 1
                end_index = unit['sell_last_executed_index']
                raw_section = raw_df.loc[start_index:end_index] 
                over_target_df = raw_section[raw_section.price>=target_price]
                over_target_df['acc_volume'] = over_target_df['volume'].cumsum(axis = 0)
                if (over_target_df.acc_volume >= float(p['max_order'])).any():
                    last_target_index = over_target_df[over_target_df.acc_volume >= float(p['max_order'])].iloc[0].name
                    first_stop_index = raw_section[raw_section.price <= round(stop_price,3)].iloc[0].name
                    if last_target_index > first_stop_index:
                        partition = 'L' # loser
                    else:
                        partition = 'W' # winner
                else:
                    partition = 'L' # loser

        elif unit['buy_type'] == 'nothing-bought':
            partition = 'N' # nothing-bought
        elif unit['buy_type'] == 'partially-bought':
            partition = 'P' # partiallly-bought

        candle0_event_list.append([unit["0_ts"],whether_stopped + partition])

    return candle0_event_list

def get_raw(p):
    return pd.read_csv(p['path_historical_data'], header=None, names=['timestamp','price','volume'])

def get_units_list(p):
    engine = sqlalchemy.create_engine("postgresql://postgres:spectrum@localhost/postgres")
    query = "SELECT * FROM phase1 WHERE ph1 = '{}'".format(p["ph1"])
    df = pd.read_sql_query(query,engine)
    units_dict = df.to_dict("index")
    return [value for (key,value) in units_dict.items()]

def get_parameters(case_id):
    engine = sqlalchemy.create_engine("postgresql://postgres:spectrum@localhost/postgres")
    query = "SELECT * FROM cases WHERE case_id = '{}'".format(case_id)
    df = pd.read_sql_query(query,engine)
    notYet_p = df.to_dict("list")
    p = {key:value[0] for (key,value) in notYet_p.items()}
    p["timeframe_start"] = str(p["timeframe_start"])
    p["timeframe_end"] = str(p["timeframe_end"])
    return p

def translate_order(mode,inputt):
# This function receives as inputt a string with the format '1-2-3_0high+30' and returns a list called 'candle' and
# a dictionary 'moment' that are useful for further calculation.
    moment = {}
    candle,moment['string'] = inputt.split('_')
    candle = candle.split('-')

    if mode == 'buy':
        index = 0
        for char in moment['string']:
            if char.isdigit():
                index = index + 1 
            else:
                break
        moment['candle'] = moment['string'][0:index]
        moment['ohlc'] = [i for i in ['open','high','low','close'] if i in moment['string']][0]
        ope = [i for i in ['+','-','*'] if i in moment['string']]
        if ope != []:
            moment['operator'] = ope[0]
            moment['change'] = moment['string'][moment['string'].find(moment['operator'])+1:]
        return candle,moment

    if mode == 'sell':
        return candle,moment

def get_dataframe(candle_file):
    pre_candles_df = pd.read_csv(candle_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])
    candles_df = pre_candles_df.set_index('timestamp')
    return candles_df

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))