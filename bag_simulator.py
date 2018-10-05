from pprint import pprint
import json
import secrets

def main():

    testedSetup_file = 'triplets_setup1538609561_0.02.txt'
    testedSetup = get_testedSetup(testedSetup_file)
    
    games = 200
    samples = 50
    bagPercentage = 0.05
    initialBag = 10000

    for tripletResult in testedSetup['tripletsResult']:
        P = tripletResult['events']
        triplet = tripletResult['triplet']
        omega = sum([P[event] for event in list(P)])
        for event in list(P):
            P[event] = P[event]/omega

        bag = bagPrediction(P,triplet,initialBag,bagPercentage,games,samples)
        print(triplet,': ',bag)


def bagPrediction(P,triplet,bag,bagPercentage,games,samples):
    target = triplet['target']     
    stop = triplet['stop']     
    buyStop = triplet['buyStop']  
    bagChange = {
        'TW': buyStop,
        'FW': target,
        'TL': buyStop,
        'FL': stop,
        'TC': buyStop,
        'FC': 0,
        'TN': 0,
        'FN': 0,
        'TP': 0,
        'FP': 0,
    }
    for _ in range(1,games+1):
        bag = bag*(1 - bagPercentage) + bag*bagPercentage*(1 + bagChange[roll(P)])
    return bag
    
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

def get_testedSetup(testedSetup_file):
    dir_path = 'builders/warehouse/setup_data/'
    testedSetup_path = dir_path + testedSetup_file
    with open(testedSetup_path) as f:
        return json.load(f)

if __name__ == '__main__':
    main()