from pprint import pprint
import json
import secrets
import numpy as np
import time,csv,os

def main():

    input_dict = {
        'testedSetup_file': 'triplets_setup1539116406_0.02_50.txt',
        'games': 100,
        'samples': 200,
        'bagPercentage': 1,
        'initialBag': 10000,
        'marketOrder': -0.00075,
        'limitOrder': 0.00025
    }

    p,testedSetup = get_testedSetup(input_dict['testedSetup_file'])
    p['bag_simulator'] = {key:str(value) for (key,value) in input_dict.items()}
    
    simulations_list = []

    for tripletResult in testedSetup:
        P = tripletResult['events']
        triplet = tripletResult['triplet']
        lastPrice = tripletResult['lastPrice']
        omega = sum([P[event] for event in list(P)])
        for event in list(P):
            P[event] = P[event]/omega

        triplet['average_bag'] = bagPrediction(P,triplet,lastPrice,input_dict)
        simulations_list.append(triplet)

    write_json((p,simulations_list))

def bagPrediction(P,triplet,lastPrice,input_dict):
    target = triplet['target']     
    stop = triplet['stop']     
    buyStop = triplet['buyStop']  
    bagPercentage = input_dict['bagPercentage']
    marketOrder = input_dict['marketOrder']
    limitOrder = input_dict['limitOrder']

    eventsInfo = {
        'TW': {'change': buyStop, 'entryFee': marketOrder , 'exitFee': marketOrder},
        'FW': {'change': target, 'entryFee': marketOrder , 'exitFee': limitOrder},
        'TL': {'change': buyStop, 'entryFee': marketOrder , 'exitFee': marketOrder},
        'FL': {'change': stop, 'entryFee': marketOrder , 'exitFee': marketOrder},
        'TC': {'change': buyStop, 'entryFee': marketOrder , 'exitFee': marketOrder},
        'FC': {'change': lastPrice, 'entryFee': marketOrder , 'exitFee': limitOrder},
        'TN': {'change': 0, 'entryFee': 0 , 'exitFee': 0},
        'FN': {'change': 0, 'entryFee': 0 , 'exitFee': 0},
        'TP': {'change': buyStop, 'entryFee': marketOrder , 'exitFee': marketOrder},
        'FP': {'change': stop, 'entryFee': marketOrder , 'exitFee': marketOrder}
    }
    simulated_bags = []
    for _ in range(input_dict['samples']):
        bag = input_dict['initialBag']
        for _ in range(input_dict['games']):
            event_game = eventsInfo[roll(P)]
            entryFee = event_game['entryFee']
            exitFee = event_game['exitFee']
            change = event_game['change']
            
            bag = bag*(1 - bagPercentage) + bag*bagPercentage*(1 + change) + bag*bagPercentage*entryFee + bag*bagPercentage*exitFee
            simulated_bags.append(bag)
    return np.mean(simulated_bags)
    
def roll(P):
    randRoll = secrets.SystemRandom().random() # in [0,1)
    sum = 0
    result = 0
    resultList = list(P)
    massDist = [P[event] for event in list(P)]
    for mass in massDist:
        sum += mass
        if randRoll < sum:
            return resultList[result]
        result+=1

def write_json(data):
    # It dumps the data in a new file called "experiment<ts_now>.txt" in experiment_data directory.
    firstPart = 'builders/warehouse/setup_data/simulation'
    secondPart = str(int(time.time()))
    path = firstPart + '_' + secondPart + '.txt'
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

if __name__ == '__main__':
    main()