import json
import json
import secrets
import numpy as np
import time,csv,os,datetime
from pprint import pprint
from tqdm import tqdm
import pandas as pd

def main():
    dir_path = 'builders/warehouse/setup_data/'
    simulation = 'simulation_1540319594_0.02_50_25_1_10000_bitmex.txt'
    testedSetup_path = dir_path + simulation
    p,data = read_json(testedSetup_path)

    pt1= simulation.split('_')[1]
    pt2 = simulation.split('_')[2]
    pt3 = simulation.split('_')[3]
    total = 'triplets_setup' + pt1 + '_' + pt2 + '_' + pt3 + '.txt'
    testedSetup_path2 = dir_path + total
    p1,data1 = read_json2(testedSetup_path2)
    x = find_event(data,data1,p,pt2)
    pprint(x)
    # higher_avgBag(x)


def higher_avgBag(x):
    df = pd.DataFrame(x)
    q = df.iloc[df.average_bag.idxmax()]
    # with open('combined_file.csv', 'wb') as outcsv:
    # writer = csv.writer(outcsv)
    # writer.writerow(["Date", "temperature 1", "Temperature 2"])
    with open('builders/warehouse/teste2.csv', 'w', newline='') as file:
        spamwriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # spamwriter.writerow(['FC','FL','FN','FP','FW','TC','TL','TN','TP','TW','amount','average_bag','buyStop','stop','target'])
        spamwriter.writerow(q)
    # q.to_csv('builders/warehouse/teste.csv', encoding='utf-8', index=False)
    print(q)


def find_event(data,data1,p,pt2):
    x = []
    for i in tqdm(data):
        if i['average_bag'] > 10400 :
            # print(i)
            target = i['target']
            stop = i['stop']
            buyStop = i['buyStop']
            for j in data1:
                if j['events']['FL'] > 10 and j['triplet']['target'] == target and j['triplet']['stop'] == stop and j['triplet']['buyStop'] == buyStop and :
                    dtc = {**i, **j['events'],'amount': p['units_amt'],'id':pt2,'space':p['space'],'buy':p['buy'],'sell':p['sell'],**{key:value for (key,value) in x.items() if key not in ["F1_above_path_candle_file","F1_below_path_candle_file"]}}
                    x.append(dtc)
                    # print(i)
                    # print(j['events'])
                    target = 0
                    stop = 0
                    buyStop = 0   
    # print(p['units_maker']['units_amt'])
    # print(x)
    return x

def read_json(testedSetup_path):
    with open(testedSetup_path) as f:
        return json.load(f)   

def read_json2(testedSetup_path2):
    with open(testedSetup_path2) as f:
        return json.load(f)

# half1 = 'builders/warehouse/'
# half2 = 'AAAAAAAAAAAAAAAA'
# path = half1 + half2 + '.csv'


# def write_csv(path,data):
#     with open(path, 'a', newline ='') as employee_file:
#         employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

#         employee_writer.writerow(data)
#     # employee_writer.writerow(['Erica Meyers', 'IT', 'March'])


# def create_df():
#     df = pd.DataFrame()
#     # list1 = [1,2,3]
#     # list2 = [4,5,6]
#     # df['o'] = list1
#     # df['p'] = list2
#     info_array = np.zeros([df,2])
#     info_array[:,0] =
#     # td_array[:,0] = df['o']
#     # return td_array
#     a = 'c'
#     b = 'b'
#     return a
# data = create_df()
# write_csv(path,data)


if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
