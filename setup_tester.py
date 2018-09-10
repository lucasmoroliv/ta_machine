import json,time,datetime
from pprint import pprint
import pandas as pd
import numpy as np

def main():
    # setup_file = 'setup1536585998.txt'
    setup_file = 'setup1536586748.txt'
    p,units_list = get_setup(setup_file)
    # pprint(p)
    # pprint(units_list)
    # raw_df= get_raw(p)
    raw_df = 5
    result = test_setup(units_list,raw_df,0.007,-0.0035)
    pprint(result)

def test_setup(units_list,raw_df,target,stop):

    result = {
        'all_units': {
            'total': len(units_list)
        },
        'traded_units': {
            'winner': 0,
            'consolidation': 0,
            'loser': 0,
            'both-winner-loser': 0
        }
    }
    for unit in units_list:
# First thing, it checks what is the type of the unit and updates a counter so the key 'all_units' of the
# dictionary gets the amount of each unit type in the setup.
        if unit['type'] not in result['all_units']:
            result['all_units'][unit['type']] = 0
        result['all_units'][unit['type']] = result['all_units'][unit['type']] + 1 
# Next we need to assign the units with type 'all_sold' as 'winner', 'loser', or 'consolidation'.

        if unit['type'] == 'all-sold':
            if unit['sell']['realHighest'] >= target and unit['lowest']['price'] > stop:
                result['traded_units']['winner'] = result['traded_units']['winner'] + 1
            if unit['sell']['realHighest'] < target and unit['lowest']['price'] > stop:
                result['traded_units']['consolidation'] = result['traded_units']['consolidation'] + 1
            if unit['sell']['realHighest'] < target and unit['lowest']['price'] <= stop:
                result['traded_units']['loser'] = result['traded_units']['loser'] + 1
# If the next condition is met, some further investigation is needed before concluding whether the unit is 
# 'winner' or 'loser'.
            if unit['sell']['realHighest'] >= target and unit['lowest']['price'] <= stop:
                result['traded_units']['both-winner-loser'] = result['traded_units']['both-winner-loser'] + 1
            #     start_index = unit['buy']['last_executed']['index'] + 1
            #     end_index = unit['sell']['last_executed']['index']
            #     raw_unit = raw_df.loc[start_index:end_index]                
            #     index_target_hit = raw_df[] 
            #     index_stop_hit = raw_df[]

    return result




def get_raw(p):
    return pd.read_csv(p['unit_maker']['path_historical_data'], header=None, names=['timestamp','price','volume'])
    
def get_setup(setup_file):
    dir_path = 'builders/warehouse/setup_data/'
    setup_path = dir_path + setup_file
    with open(setup_path) as f:
        return json.load(f)

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))