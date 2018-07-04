import numpy as np
import pandas as pd
import time,calendar,datetime,csv,math,json
from pprint import pprint
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn.model_selection import train_test_split

def callable(dict_arrays,info_as_feature,labels_list,min_profit):
    # features_list = features_list_maker(info_as_feature,dict_arrays)
    features_array = data_maker(dict_arrays,features_list)
    print(features_list)

    # floated_labels_array = data_maker(dict_arrays,labels_list)
    # labels_array = into_labels(floated_labels_array,min_profit)
    # labels_array = labels_array.ravel()
    # features_train, features_test, labels_train, labels_test = train_test_split(features_array,labels_array, test_size=0.2, random_state=42)
    # print(features_array)
    # print(labels_array)


    # print(features_train)
    # print(labels_train)
    # print(features_test)
    # print(labels_test)
    # score = gaussian_classifier(features_train, labels_train, features_test, labels_test)
    # return score

def into_labels(floated_labels_array,min_profit):
    return (floated_labels_array>min_profit).astype(int)

def data_maker(lists,info_list):
    df = pd.DataFrame(lists)
    return df[info_list].copy().values

def features_list_maker(info_list,lists):
    keys = list(lists.keys())
    candle_amt = 0
    features_list = []
    for key in keys:
        if 'ts' in key:
            candle_amt = candle_amt + 1
    for info in info_list:
        for candle in range(1,candle_amt+1):
            features_list.append('candle_{0}_{1}'.format(candle,info))
    return features_list

def svm_classifier(features_train, labels_train, features_test, labels_test):
    clf = svm.SVC(kernel='rbf', gamma=10, C=1000)
    clf.fit(features_train, labels_train)
    return clf.score(features_test, labels_test)

def gaussian_classifier(features_train, labels_train, features_test, labels_test):
    clf = GaussianNB()
    clf.fit(features_train, labels_train)
    return clf.score(features_test, labels_test)

def decisiontree_classifier(features_train, labels_train, features_test, labels_test):
    clf = tree.DecisionTreeClassifier()
    clf.fit(features_train, labels_train)
    return clf.score(features_test, labels_test)

def main():
    df_file = '30min_bitstamp.csv'
    object_file = 'data.txt'
    timeframe = ['2017-05-10 00:00:00','2018-04-20 00:00:00']
    goodtimes = goodtimes1_1.callable(object_file,timeframe)
    lists = pattern1_1.callable(goodtimes,df_file)
    # pprint(lists)
    info_as_feature = ['rsi']
    features_list = features_list_maker(info_as_feature,lists)
    labels_list = ['candle_4_high']
    features_array = data_maker(lists,features_list)
    floated_labels_array = data_maker(lists,labels_list)
    labels_array = into_labels(floated_labels_array)
    labels_array = labels_array.ravel()
    features_train, features_test, labels_train, labels_test = train_test_split(features_array,labels_array, test_size=0.2, random_state=42)
    x = gaussian_classifier(features_train, labels_train, features_test, labels_test)
    print(x)

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
