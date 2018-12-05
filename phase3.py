from pprint import pprint
import json,sqlalchemy,secrets,time,csv,os,collections,psycopg2,logging
import numpy as np
import pandas as pd
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def main():
    engines_door(2)

def engines_door(case_id):
    logger.info("Running case_id {}".format(case_id))
    time1 = time.time()
    p = get_parameters(case_id) 
    testedSetups = get_testedSetups(p)
    simulations = get_simulations(p,testedSetups)
    insertInto_phase3(simulations,"phase3",p["ph3"])
    update_state(case_id)
    logger.info("case_id {} is completed in {} seconds.".format(case_id,time.time()-time1))

def bagPrediction(p,events,setup,last_price):
    candle,moment = translate_order('buy',p['buy'])
    target = setup['target']     
    stop = setup['stop']     
    buy_stop = setup['buy_stop']  
    bag_percentage = p['bag_percentage']
    market_order = p['market_order']
    limit_order = p['limit_order']

    # eventsInfo in case change is either not existent or >= than 1.
    if not "operator" in moment or float(moment["change"]) >= 1:
        eventsInfo = {
            'TW': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FW': {'change': target, 'entryFee': market_order, 'exitFee': limit_order},
            'TL': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FL': {'change': stop, 'entryFee': market_order, 'exitFee': market_order},
            'TC': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FC': {'change': last_price, 'entryFee': market_order, 'exitFee': market_order},
            'TN': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FN': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'TP': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FP': {'change': 0, 'entryFee': 0, 'exitFee': 0} # There will be no FP events in such case.
        }
    # eventsInfo in case change is < than 1.
    elif float(moment["change"]) < 1:
        eventsInfo = {
            'TW': {'change': buy_stop, 'entryFee': limit_order, 'exitFee': market_order},
            'FW': {'change': target, 'entryFee': limit_order, 'exitFee': limit_order},
            'TL': {'change': buy_stop, 'entryFee': limit_order, 'exitFee': market_order},
            'FL': {'change': stop, 'entryFee': limit_order, 'exitFee': market_order},
            'TC': {'change': buy_stop, 'entryFee': limit_order, 'exitFee': market_order},
            'FC': {'change': last_price, 'entryFee': limit_order, 'exitFee': market_order},
            'TN': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'FN': {'change': 0, 'entryFee': 0, 'exitFee': 0},
            'TP': {'change': buy_stop, 'entryFee': limit_order, 'exitFee': market_order},
            'FP': {'change': stop, 'entryFee': limit_order, 'exitFee': market_order}
        } 

    simulated_bags = []
    for _ in range(p['samples']):
        bag = p['initial_bag']
        for _ in range(p['games']):
            event_game = eventsInfo[roll(events)]
            entryFee = event_game['entryFee']
            exitFee = event_game['exitFee']
            change = event_game['change']
            bag = bag*(1 - bag_percentage) + bag*bag_percentage*(1 + change) + bag*bag_percentage*entryFee + bag*bag_percentage*exitFee
            simulated_bags.append(bag)
    return np.median(simulated_bags),np.mean(simulated_bags),np.min(simulated_bags),np.max(simulated_bags)

def get_simulations(p,testedSetups):
    simulations = []
    for testedSetup in testedSetups:
        events = {key:value for (key,value) in testedSetup.items() if len(key) == 2 and key.isupper()}
        omega = sum([events[event] for event in list(events)])
        for event in list(events):
            events[event] = events[event]/omega
        setup = {
            "target": testedSetup["target"],
            "stop": testedSetup["stop"],
            "buy_stop": testedSetup["buy_stop"]
        }
        last_price = testedSetup["last_price"]
        setup["median_bag"],setup["average_bag"],setup["min_bag"],setup["max_bag"] = bagPrediction(p,events,setup,last_price)
        setup["median_bag"] = (setup["median_bag"]-p["initial_bag"])/p["initial_bag"]
        setup["average_bag"] = (setup["average_bag"]-p["initial_bag"])/p["initial_bag"]
        setup["min_bag"] = (setup["min_bag"]-p["initial_bag"])/p["initial_bag"]
        setup["max_bag"] = (setup["max_bag"]-p["initial_bag"])/p["initial_bag"]
        simulations.append(setup)
    return simulations

def roll(events):
    randRoll = secrets.SystemRandom().random() # in [0,1)
    sum = 0
    result = 0
    resultList = list(events)
    massDist = [events[event] for event in list(events)]
    for mass in massDist:
        sum += mass
        if randRoll < sum:
            return resultList[result]
        result+=1

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    p = data[0]
    firstPart = 'builders/warehouse/setup_data/simulation'
    secondPart = p['setup_file'].split('.')[0][5:] #str(int(time.time()))
    thirdPart = p['space']
    fourthPart = p['percentile_last_price']
    fifthPart = p['games']
    sixthPart = p['bag_percentage']
    seventhPart = p['initial_bag']
    eightPart = 'bitmex'
    path = firstPart + '_' + secondPart +'_' + thirdPart + '_' + fourthPart + '_' + fifthPart + '_' + sixthPart + '_' + seventhPart + '_' + eightPart + '.txt'
    if os.path.exists(path):
        print('There is already a file with this name.')
    else:
        with open(path, 'w') as outfile:
            json.dump(data, outfile)        

def get_testedSetup(testedSetup_file):
    dir_path = 'builders/warehouse/setup_data/'
    testedSetup_path = dir_path + testedSetup_file
    with open(testedSetup_path) as f:
        return json.load(f)

def get_testedSetups(p):
    engine = sqlalchemy.create_engine("postgresql://postgres:spectrum@localhost/postgres")
    query = "SELECT * FROM phase2 WHERE ph2 = '{}'".format(p["ph2"])
    df = pd.read_sql_query(query,engine) 
    units_dict = df.to_dict("index")
    return [value for (key,value) in units_dict.items()]

def insertInto_phase3(units_list,table_name,ph3):
    success = False
    while not success:
        try:
            df = dataframing(units_list)
            add_column(df,'ph3',ph3)
            engine = sqlalchemy.create_engine("postgresql://postgres:spectrum@localhost/postgres")
            df.to_sql(
                name = table_name,
                con = engine,
                if_exists = 'append'
            )
            success = True
        except:
            time.sleep(random.randint(3,6))

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
    engine = sqlalchemy.create_engine("postgresql://postgres:spectrum@localhost/postgres")
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
            password = 'spectrum'
            conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
            c = conn.cursor()
            c.execute("SELECT ph3 FROM cases WHERE case_id = {}".format(case_id))
            phase_hash = c.fetchone()[0]
            c.execute("UPDATE cases SET state = 'ph3' WHERE ph3 = '{}'".format(phase_hash))
            conn.commit()
            success = True
        except:
            time.sleep(random.randint(3,6))

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

if __name__ == '__main__':
    main()