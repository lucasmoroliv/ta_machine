# This file is part of ta_machine.

# ta_machine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ta_machine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ta_machine.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json,sys,operator,os,sqlalchemy,collections,psycopg2,logging,re
from pprint import pprint
from builders import momentum_indicators 
import chart_filter
import filter1
import random
pd.options.mode.chained_assignment = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

class ZeroUnitsError(Exception):
    pass

def main():
    engines_door(3)
    
def engines_door(case_id):
    logger.info("Running case_id {}".format(case_id))
    time1 = time.time()
    p = get_parameters(case_id)
    if p["filter"] == None:
        goodtimes = [[calendar.timegm(time.strptime((p['timeframe_start']), '%Y-%m-%d %H:%M:%S')),calendar.timegm(time.strptime(p['timeframe_end'], '%Y-%m-%d %H:%M:%S'))]]
    else:    
        goodtimes = globals()[p["filter"]].frontDoor(p)
    units_list = get_units_list(p,goodtimes)
    if len(units_list) == 0:
        raise ZeroUnitsError
    insertInto_phase1(units_list,"phase1",p["ph1"])
    update_state(case_id)
    logger.info("case_id {} is completed in {} seconds.".format(case_id,time.time()-time1))

def get_units_list(p,goodtimes):
    candle_df = get_dataframe(p["path_candle_file"])
    raw_df = get_raw(p)
    units_list = globals()[p['pattern']](p,goodtimes)
    action_dict = {}
    for item in ['buy','sell','lowest','last_price']:
        globals()['add_{0}'.format(item)](p,units_list,candle_df,raw_df,action_dict)
    return units_list

# ---------------------------------------------------------------------------------
# * SECTION 1 *
# Every function in this section must return a units_list, with the timestamp of the candle 0 of each unit. 

def pattern1(p,goodtimes):
    # Input: <p>, specifically p['path_candle_file'] and p['p1_threshold']. <goodtimes> which has all the periods we want. In case chart_filter turned off, <goodtimes> will be a list containing
    # one period, which is a list of two items, the first being the inferior limit and the second the superior limit of the period. In the other hand, if chart_filter is turned on, <goodtimes> will most likely have
    # many periods in it.
    # Output: <units_list>, which is a list of dictionaries. Each dictionary only has the '0' key, which stands for 'candle 0'. Its value is also a dictionary with a single key named 'ts' containing the timestamp
    # of the candle 0 as a value. <units_list> can be understood as a list of units. Every single dictionary in the list is a place where will be added the respective information of each unit. So far in the program
    # the only information each unit has is its first timestamp, the timestamp that starts the candle 0.       
    rsi = momentum_indicators.rsi(p['path_candle_file'])
    units_list = []
    threshold = float(p['p1_threshold'])
    for period in goodtimes: 
        mini_rsi = filter_rsi(rsi,period)
        for index in range(mini_rsi.shape[0]):
            if mini_rsi[index,1] < threshold and mini_rsi[index-1,1] > threshold:
                units_list.append({'0': {'ts': mini_rsi[index,0]}})
    return units_list

def pattern2(p,goodtimes):
    # For td_setup : equal to 9 for "normal" td_sell_setup, 80 for minimal_sell_setup or 90 for perfect_sell_setup
    #              : equal to -9 for "normal" td_buy_setup, -80 for minimal_buy_setup or -90 for perfect_sell_setup
    td_s_df = get_td_s_df(p)
    td_s_df = td_s_df.reset_index()
    td = td_s_df.values
    td_s = int(p['p2_td_s'])
    units_list = []
    for period in goodtimes: 
        mini_td = filter_td(td,period)
        for i in range(mini_td.shape[0]):
            if mini_td[i,1]==td_s:
                units_list.append({'0': {'ts': mini_td[i,0]}})
    return units_list

def pattern3(p,goodtimes):
    # For td_countdown : equal to 13 for td_sell_countdown
    #                  : equal to -13 for td_buy_countdown
    td_c_df = get_td_c_df(p)
    td_c_df = td_c_df.reset_index()
    td = td_c_df.values
    td_c = int(p['p3_td_c'])
    units_list = []
    for period in goodtimes: 
        mini_td = filter_td(td,period)
        for i in range(mini_td.shape[0]):
            if mini_td[i,1]==td_c:
                units_list.append({'0': {'ts': mini_td[i,0]}})
    return units_list

def pattern4(p,goodtimes):
    shorter_rsi = momentum_indicators.rsi(p['path_candle_file'])
    maybe_candle0_list = []
    for period in goodtimes: 
        mini_rsi = filter_rsi(shorter_rsi,period)
        for index in range(mini_rsi.shape[0]):
            if mini_rsi[index,1] < float(p['p4_shorter_rsi']) and mini_rsi[index-1,1] > float(p['p4_shorter_rsi']):
                maybe_candle0_list.append(mini_rsi[index,0])
    return check_longer_rsi(p,maybe_candle0_list)

# ---------------------------------------------------------------------------------
# * SECTION 2 *
# Add details to units_list for further analysis.

def add_buy(p,units_list,candle_df,raw_df,action_dict):
    operator_dict = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul
    }
    candle,moment = translate_order('buy',p['buy'])
    action_dict['buy'] = {
        'candle': candle,
        'moment': moment
    }
    candle,moment = translate_order('sell',p['sell'])
    action_dict['sell'] = {
        'candle': candle,
        'moment': moment
    }
    for unit in units_list:
        unit['buy'] = {}
        find_buy(p,unit,candle_df,raw_df,operator_dict,action_dict)

def add_sell(p,units_list,candle_df,raw_df,action_dict):
    for unit in units_list:
        if unit['buy']['type'] == 'all-bought':
            unit['sell'] = {}
            find_sell(p,unit,candle_df,raw_df,action_dict)

def add_lowest(p,units_list,candle_df,raw_df,action_dict):
    for unit in units_list:
        if unit['buy']['type'] == 'all-bought':
            if unit['sell']['type'] == 'all-sold':
                unit['lowest'] = {}
                find_lowest(p,unit,candle_df,raw_df)

def add_last_price(p,units_list,candle_df,raw_df,action_dict):
    for unit in units_list:
        end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(action_dict['sell']['candle'][-1])+1)
        raw_section = raw_df[raw_df.timestamp<end_interval]    
        unit['last_price'] = (raw_section.iloc[-1].price - unit['buy']['price'])/unit['buy']['price']

# ---------------------------------------------------------------------------------
# * SECTION 3 *
# Here is a space to store all sorts of auxiliary functions.

def find_buy(p,unit,candle_df,raw_df,operator_dict,action_dict):
    unit['buy']['price'] = candle_df.loc[int(unit['0']['ts'])+int(p['candle_sec'])*int(action_dict['buy']['moment']['candle'])][action_dict['buy']['moment']['ohlc']]
    if 'operator' in action_dict['buy']['moment']:
        unit['buy']['price'] = operator_dict[action_dict['buy']['moment']['operator']](float(unit['buy']['price']),float(action_dict['buy']['moment']['change']))  
    start_interval = int(unit['0']['ts'])+int(p['candle_sec'])*int(action_dict['buy']['candle'][0])
    if action_dict['buy']['candle'][-1] == 'sellEnd':
        end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(action_dict['sell']['candle'][-1])+1)
    else:
        end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(action_dict['buy']['candle'][-1])+1) 
    raw_section = raw_df[(raw_df.timestamp>=start_interval) & (raw_df.timestamp<end_interval)]    
    lowest_of_section = raw_section[raw_section.price == raw_section.price.min()].iloc[0]
    unit['buy']['lowest'] = {
        'ts': int(lowest_of_section.timestamp), 
        'index': int(lowest_of_section.name),
        'price': (float(lowest_of_section.price) - unit['buy']['price'])/unit['buy']['price']
    }
    raw_partition = raw_section[raw_section.price>=unit['buy']['price']]
    if raw_partition.empty:
        unit['buy']['type'] = 'nothing-bought'
        return
    raw_partition['USD_acc_volume'] = raw_partition['volume'].cumsum(axis = 0)*raw_partition['price']
    unit['buy']['first_executed'] = {
        'ts': int(raw_partition.iloc[0].timestamp),
        'index': int(raw_partition.iloc[0].name)
    }
    if (raw_partition.USD_acc_volume >= float(p['max_order'])).any():
        unit['buy']['type'] = 'all-bought'
        last_executed_row = raw_partition[raw_partition.USD_acc_volume >= float(p['max_order'])].iloc[0]
        unit['buy']['last_executed'] = {
            'ts': int(last_executed_row.timestamp),
            'index': int(last_executed_row.name)
        }
        start_interval_to_last_executed = raw_section.loc[:unit['buy']['last_executed']['index']]
        lowest_row = start_interval_to_last_executed[start_interval_to_last_executed.price == start_interval_to_last_executed.price.min()].iloc[0]
        unit['buy']['lowest'] = {
            'ts': int(lowest_row.timestamp), 
            'index': int(lowest_row.name),
            'price': (float(lowest_row.price) - unit['buy']['price'])/unit['buy']['price']
        }
    else:
        unit['buy']['type'] = 'partially-bought'

def find_sell(p,unit,candle_df,raw_df,action_dict):
    start_index = unit['buy']['last_executed']['index']
    end_interval = int(unit['0']['ts'])+int(p['candle_sec'])*(int(action_dict['sell']['candle'][-1])+1)
    raw_section = raw_df[(raw_df.index>start_index) & (raw_df.timestamp<end_interval)]    
    raw_sorted = raw_section.sort_values(by=['price'],ascending=False)
    
    if raw_sorted.empty:
        unit['sell']['type'] = 'nothing-sold'
        return
    else:
        unit['sell']['type'] = 'partially-sold'
        raw_sorted['USD_acc_volume'] = raw_sorted['volume'].cumsum(axis = 0)*raw_sorted['price']

    if (raw_sorted.USD_acc_volume >= float(p['max_order'])).any():
        unit['sell']['type'] = 'all-sold'
        realhighest_price = raw_sorted[raw_sorted.USD_acc_volume >= float(p['max_order'])].iloc[0].price
        unit['sell']['realhighest_price'] = realhighest_price
        unit['sell']['realhighest'] = (float(realhighest_price) - unit['buy']['price'])/unit['buy']['price']

        raw_partition = raw_section[raw_section.price>=realhighest_price]
        raw_partition['USD_acc_volume'] = raw_partition['volume'].cumsum(axis = 0)*raw_partition['price']
        last_row = raw_partition[raw_partition.USD_acc_volume >= float(p['max_order'])].iloc[0]
        unit['sell']['first_executed'] = {
            'ts': int(raw_partition.iloc[0].timestamp), 
            'index': int(raw_partition.iloc[0].name) 
        }
        unit['sell']['last_executed'] = {
            'ts': int(last_row.timestamp), 
            'index': int(last_row.name) 
        }

def find_lowest(p,unit,candle_df,raw_df):
    start_index = unit['buy']['last_executed']['index'] + 1
    end_index = unit['sell']['last_executed']['index']
    raw_section = raw_df.loc[start_index:end_index]    
    min_row = raw_section[raw_section.price == raw_section.price.min()].iloc[0]
    unit['lowest']['price'] = (float(min_row.price) - unit['buy']['price'])/unit['buy']['price']
    unit['lowest']['ts'] = int(min_row.timestamp)
    unit['lowest']['index'] = int(min_row.name)

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

def get_raw(p):
    return pd.read_csv(p['path_historical_data'], header=None, names=['timestamp','price','volume'])

def filter_rsi(rsi,timeframe):
    return rsi[(rsi[:,0] >= timeframe[0]) & (rsi[:,0] <= timeframe[1])]

def filter_td(td,timeframe):
    return td[(td[:,0] >= timeframe[0]) & (td[:,0] <= timeframe[1])]

def get_dataframe(candle_file):
    pre_candles_df = pd.read_csv(candle_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])
    candles_df = pre_candles_df.set_index('timestamp')
    return candles_df


def get_rsi_df(p):
    rsi_array = momentum_indicators.rsi(p['path_candle_file'])
    pre_rsi_df = pd.DataFrame(rsi_array, columns = ['timestamp','rsi'])
    rsi_df = pre_rsi_df.set_index('timestamp')
    return rsi_df

def get_td_s_df(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open('builders/warehouse/td_data/td_setup_{}.csv'.format(get_name(p["path_candle_file"])), newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        td_s_data = np.array(big_list)
        # td_s_data = td_s_data.astype(int)
    td_s_df = pd.DataFrame(td_s_data, columns = ['timestamp','td_s'])
    td_s_df = td_s_df.set_index('timestamp')
    return td_s_df

def get_name(string):
    index = [m.start() for m in re.finditer('/', string)][-1]
    return string[index+1:-4]

def get_td_c_df(p):
# Here we get the data from the csv and put in an array the timestamp and the td of the respective candle
    with open('builders/warehouse/td_data/td_countdown_{}.csv'.format(get_name(p["path_candle_file"])), newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        list = []
        big_list = []
        for row in data:
            ts_start = float(row[0].split(',')[0])
            td = float(row[0].split(',')[1])
            big_list.append([ts_start,td])
        td_c_data = np.array(big_list)
        # td_c_data = td_c_data.astype(int)
    td_c_df = pd.DataFrame(td_c_data, columns = ['timestamp','td_c'])
    td_c_df = td_c_df.set_index('timestamp')
    return td_c_df

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    half1_path = 'builders/warehouse/setup_data/setup'
    half2_path = str(int(time.time()))
    path = half1_path + half2_path + '.txt'
    while os.path.exists(path):
        time.sleep(1)
        half2_path = str(int(time.time()))
        path = half1_path + half2_path + '.txt'
    with open(path, 'w') as outfile:
        json.dump(data, outfile)

def insertInto_phase1(units_list,table_name,ph1):
    success = False
    while not success:
        try:
            df = dataframing(units_list)
            add_column(df,'ph1',ph1)
            engine = sqlalchemy.create_engine("postgresql://postgres:DarkZuoqson-postgresql32229751!@localhost/postgres")
            df.to_sql(
                name = table_name,
                con = engine,
                if_exists = 'append'
            )
            success = True
        except:
            time.sleep(3)

def dataframing(units_list):
    # It receives as input the units_list and turns it into a dataframe, which is compatible to be inserted into
    # the pandas method to_sql.

    # We need to flatten all the dictionaries of units_list. Since the dictionaries have many keys with equal
    # names, the keys in the flatten state will be changed in clever way that is short but makes it distint from
    # each other.
    for i in range(len(units_list)):
        units_list[i] = flatten(units_list[i])
    return pd.DataFrame(units_list)
        
def add_column(df,column_name,filler):
    # Add column to the dataframe df. Every cell of the column will have the value filler.
    new_column = np.full((df.shape[0],1),filler)
    df[column_name] = new_column
    
def flatten(d, parent_key='', sep='_'):
    # It transforms a dictionary with multiple hierarchies to a flat one, where key only contain values that
    # don't include other keys.
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_parameters(case_id):
    engine = sqlalchemy.create_engine("postgresql://postgres:DarkZuoqson-postgresql32229751!@localhost/postgres")
    query = "SELECT * FROM cases WHERE case_id = '{}'".format(case_id)
    df = pd.read_sql_query(query,engine)
    notYet_p = df.to_dict("list")
    p = {key:value[0] for (key,value) in notYet_p.items()}
    p["timeframe_start"] = str(p["timeframe_start"])
    p["timeframe_end"] = str(p["timeframe_end"])
    return p

def update_state(case_id):
    success = False
    while not success:
        try:
            dbname = 'postgres'
            user = 'postgres'
            host = 'localhost'
            password = 'DarkZuoqson-postgresql32229751!'
            conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
            c = conn.cursor()
            c.execute("SELECT ph1 FROM cases WHERE case_id = {}".format(case_id))
            phase_hash = c.fetchone()[0]
            c.execute("UPDATE cases SET state = 'ph1' WHERE ph1 = '{}'".format(phase_hash))
            conn.commit()
            success = True
        except:
            time.sleep(3)

def check_longer_rsi(p,maybe_candle0_list):
    # INPUT
    # p: case parameteres.
    # maybe_candle0_list: list with timestamp of candles that have rsi dropping below <p4_shorter_rsi>.
    # OUTPUT
    # It returns units_list, which is a partition of maybe_candle0_list (the candles that are under the requisits of of the longer_rsi) in a dictionary-like format. 
    units_list = []
    longer_ts_array = momentum_indicators.rsi(p['p4_longer_path_candle_file'])[:,0]
    candle_sec = longer_ts_array[1] - longer_ts_array[0]
    for maybe_candle0 in maybe_candle0_list:
        ts_longer_candle = longer_ts_array[longer_ts_array<=maybe_candle0][-1]
        close_of_candle = find_close_of_candle(maybe_candle0,p["path_candle_file"])        
        rsi_longer_candle = momentum_indicators.new_close_rsi(ts_longer_candle,p['p4_longer_path_candle_file'],close_of_candle)
        if rsi_longer_candle >= int(p["p4_longer_rsi_min"]) and rsi_longer_candle <= int(p["p4_longer_rsi_max"]):
            units_list.append({'0': {'ts': maybe_candle0}})
    return units_list

def find_close_of_candle(candle_ts,candle_file):
    df = get_dataframe(candle_file)
    # return float(df[df.timestamp == candle_ts]["close"])
    return float(df.loc[candle_ts]["close"])

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))