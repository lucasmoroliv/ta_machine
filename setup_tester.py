import json,time,datetime,itertools,os
from pprint import pprint
import pandas as pd
import numpy as np
from tqdm import tqdm
pd.options.mode.chained_assignment = None

def main():
    input_dict = {
        'setup_file': 'setup1540344830.txt',
        'space': 0.02,
        'percentile_toggle': False, # BOOLEAN
        'average_toggle': True, # BOOLEAN
        'percentile_lastPrice': 50 # INTEGER
    }
    p,units_list = get_setup(input_dict['setup_file'])
    triplets_list = get_triplets(units_list,input_dict['space']) 
    raw_df = get_raw(p)

    [str(item) for item in list(input_dict)]
    p.update({key:str(value) for (key,value) in input_dict.items()})

    testedSetup = []

    for triplet in tqdm(triplets_list):
        testedSetup.append(get_tripletsResult(p,raw_df,units_list,triplet))

    write_json((p,testedSetup))

def get_triplets(units_list,space):
    buyLowest_list = []
    lowest_list = []
    realHighest_list = []
    
    for unit in units_list:
        buyLowest_list.append(unit['buy']['lowest']['price'])
        if unit['buy']['type'] == 'all-bought':
            realHighest_list.append(unit['sell']['realHighest'])
            lowest_list.append(unit['lowest']['price'])
        else:
            realHighest_list.append(None)
            lowest_list.append(None)

    buyLowest_list = [x for x in buyLowest_list if x is not None]
    lowest_list = [x for x in lowest_list if x is not None]
    realHighest_list = [x for x in realHighest_list if x is not None]

    lowest_buyLowest = min(buyLowest_list)
    highest_buyLowest = max(buyLowest_list)
    lowest_lowest = min(lowest_list)
    highest_lowest = max(lowest_list)
    highest_realHighest = max(realHighest_list)

    if highest_lowest > 0:
        highest_lowest = 0
    if highest_buyLowest > 0:
        highest_buyLowest = 0

    target_ite = list(np.arange(0.006,highest_realHighest,space))
    stop_ite = list(np.arange(lowest_lowest,highest_lowest,space))
    buyStop_ite = list(np.arange(lowest_buyLowest,highest_buyLowest,space))

    triplets_list = [target_ite,stop_ite,buyStop_ite]
    return list(itertools.product(*triplets_list))

def get_tripletsResult(p,raw_df,units_list,triplet):
    target = triplet[0]
    stop = triplet[1]
    buyStop = triplet[2]
    setup = {
        'events': {
            'TW': 0,
            'TC': 0,
            'TL': 0,
            'TP': 0,
            'TN': 0,
            'FW': 0,
            'FC': 0,
            'FL': 0,
            'FP': 0,
            'FN': 0,
        },
        'triplet': {
            'target': target,
            'stop': stop,
            'buyStop': buyStop,
        }
    }
    aux_list = []
    lastPrice_list = []
    for unit in units_list:
        if unit['buy']['lowest']['price'] <= buyStop:
            whether_stopped = 'T' # stopped
        else: 
            whether_stopped = 'F' # not-stopped

        if unit['buy']['type'] == 'all-bought':
            if unit['sell']['realHighest'] >= target and unit['lowest']['price'] > stop:
                partition = 'W' # winner
            if unit['sell']['realHighest'] < target and unit['lowest']['price'] > stop:
                partition = 'C' # consolidation
            if unit['sell']['realHighest'] < target and unit['lowest']['price'] <= stop:
                partition = 'L' # loser
            if unit['sell']['realHighest'] >= target and unit['lowest']['price'] <= stop:
                target_price = unit['buy']['price']*(1+target)
                stop_price = unit['buy']['price']*(1+stop)
                start_index = unit['buy']['last_executed']['index'] + 1
                end_index = unit['sell']['last_executed']['index']
                raw_section = raw_df.loc[start_index:end_index] 
                over_target_df = raw_section[raw_section.price>=target_price]
                over_target_df['acc_volume'] = over_target_df['volume'].cumsum(axis = 0)
                if (over_target_df.acc_volume >= float(p['max_order'])).any():
                    last_target_index = over_target_df[over_target_df.acc_volume >= float(p['max_order'])].iloc[0].name
                    first_stop_index = raw_section[raw_section.price <= stop_price].iloc[0].name
                    if last_target_index > first_stop_index:
                        partition = 'L' # loser
                    else:
                        partition = 'W' # winner
                else:
                    partition = 'L' # loser
        if unit['buy']['type'] == 'nothing-bought':
            partition = 'N' # nothing-bought
        if unit['buy']['type'] == 'partially-bought':
            partition = 'P' # partiallly-bought

        aux_list.append(whether_stopped + partition)
        if partition == 'C':
            lastPrice_list.append(unit['lastPrice'])

    for key in set(aux_list):
        setup['events'][key] = aux_list.count(key)

    
    if p['percentile_toggle']:
        setup['lastPrice'] = np.percentile(lastPrice_list,int(p['percentile_lastPrice']))
    elif p['average_toggle']:
        setup['lastPrice'] = np.mean(lastPrice_list)
    return setup

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    firstPart = 'builders/warehouse/setup_data/triplets'
    secondPart = data[0]['setup_file'].split('.')[0]
    thirdPart = data[0]['space']
    fourthPart = data[0]['percentile_lastPrice']
    path = firstPart + '_' + secondPart + '_' + thirdPart + '_' + fourthPart + '.txt'
    if os.path.exists(path):
        print('This setup has already been tested.')
    else:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

def get_raw(p):
    return pd.read_csv(p['path_historical_data'], header=None, names=['timestamp','price','volume'])
    
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