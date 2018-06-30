import pandas as pd
import numpy as np
import time, calendar

def sma(file,num_of_candles):
    df = get_dataframe(file)
    ma_array = np.zeros([df.shape[0],2])
    for index, row in df.iterrows():
        ma_array[index,0] = row['timestamp']
        if (index+1)-num_of_candles >= 0:
            ma_array[index,1] = sum(df['close'][(index+1)-num_of_candles:(index+1)])/num_of_candles
        else:
            ma_array[index,1] = 0
    return ma_array

def ema(file,num_of_candles):
    dynamic_array = get_dataframe(file)['close'].values
    sma_array = sma(file,num_of_candles)
    multiplier = (2/(num_of_candles+1))
    ema_array = np.zeros([dynamic_array.shape[0],2])
    ema_array[:,0] = sma_array[:,0]
    for index in range(sma_array.shape[0]):
        if (index+1)-num_of_candles >= 0:
            ema_array[index,1] = (dynamic_array[index] - ema_array[index-1,1]) * multiplier + ema_array[index-1,1]
        else:
            ema_array[index,1] = 0
    return ema_array

def signal(file,shorter_ema=12,longer_ema=26,signal_ema=9):
    macd_line = (ema(file,shorter_ema)[:,1]-ema(file,longer_ema)[:,1])
    signal_line = np.zeros([macd_line.shape[0]])
    multiplier = (2/(signal_ema+1))
    for index in range(macd_line.shape[0]):
        if (index+1)-signal_ema >= 0:
            signal_line[index] = (macd_line[index] - signal_line[index-1]) * multiplier + signal_line[index-1]
        else:
            signal_line[index] = 0
    return signal_line

def macd(file,shorter_ema=12,longer_ema=26,signal_ema=9):
    df = get_dataframe(file)
    num_of_elements = ema(file,shorter_ema).shape[0]
    macd_line_array,signal_line_array,macd_histogram_array = np.zeros([num_of_elements,2]),np.zeros([num_of_elements,2]),np.zeros([num_of_elements,2])
    macd_line_array[:,0],signal_line_array[:,0],macd_histogram_array[:,0] = df['timestamp'].values,df['timestamp'].values,df['timestamp'].values
    macd_line_array[:,1] = (ema(file,shorter_ema)[:,1]-ema(file,longer_ema)[:,1])
    signal_line_array[:,1] = signal('4h_bitstamp.csv',12,26,9)
    macd_histogram_array[:,1] = (ema(file,shorter_ema)[:,1]-ema(file,longer_ema)[:,1])-signal('4h_bitstamp.csv',12,26,9)
    return {'macd_line': macd_line_array,'signal_line': signal_line_array,'macd_histogram': macd_histogram_array}

def rsi(file,choise='close',num_of_candles=14):
    dynamic_array = get_dataframe(file)[choise].values
    upward_movement,downward_movement,average_upward_movement,average_downward_movement,relative_strength = np.zeros(dynamic_array.shape[0]),np.zeros(dynamic_array.shape[0]),np.zeros(dynamic_array.shape[0]),np.zeros(dynamic_array.shape[0]),np.zeros(dynamic_array.shape[0])
    rsi = np.zeros([dynamic_array.shape[0],2])
    checker = 0
    for index in range(dynamic_array.shape[0])[1:]:
        dif = dynamic_array[index] - dynamic_array[index-1]
        if dif >= 0:
            upward_movement[index] = dif
        else:
            downward_movement[index] = abs(dif)
        if index >= num_of_candles-1:
            if checker == 0:
                average_upward_movement[index] = np.mean(upward_movement[index-(num_of_candles-1):index+1])
                average_downward_movement[index] = np.mean(downward_movement[index-(num_of_candles-1):index+1])
                checker = 1
            average_upward_movement[index] = (average_upward_movement[index-1]*(num_of_candles-1)+upward_movement[index])/num_of_candles
            average_downward_movement[index] = (average_downward_movement[index-1]*(num_of_candles-1)+downward_movement[index])/num_of_candles
            if average_downward_movement[index] == 0:
                relative_strength[index] = 0
            else:
                relative_strength[index] = average_upward_movement[index]/average_downward_movement[index]
            rsi[index,1] = 100-(100/(relative_strength[index]+1))
    rsi[:,0] = get_dataframe(file)['timestamp'].values
    return rsi

def stochastic(file,num_of_candles=14):
    high_array,low_array,close_array = np.split(get_dataframe(file)[['high','low','close']].copy().values,3,axis=1)
    array_1,array_2,percentK,slow_stochastic,signal_line = np.zeros(high_array.shape[0]),np.zeros(high_array.shape[0]),np.zeros([high_array.shape[0],2]),np.zeros([high_array.shape[0],2]),np.zeros([high_array.shape[0],2])
    for index in range(high_array.shape[0])[(num_of_candles-1):]:
        array_1[index] = close_array[index] - np.min(low_array[index-(num_of_candles-1):index+1])
        array_2[index] = np.max(high_array[index-(num_of_candles-1):index+1]) - np.min(low_array[index-(num_of_candles-1):index+1])
        percentK[index,1] = 100*array_1[index]/array_2[index]
        slow_stochastic[index,1] = 100*np.sum(array_1[index-2:index+1])/np.sum(array_2[index-2:index+1])
        signal_line[index,1] = np.mean(slow_stochastic[index-2:index+1])
    percentK[:,0],slow_stochastic[:,0],signal_line[:,0] = get_dataframe(file)['timestamp'],get_dataframe(file)['timestamp'],get_dataframe(file)['timestamp']
    return {'percentK':percentK,'slow_stochastic':slow_stochastic,'signal_line':signal_line}

    # x = np.where(percentK == 1523707200)[0]
    # print(percentK[x])
    # print(slow_stochastic[x])
    # print(signal_line[x])

def get_dataframe(file):
    return pd.read_csv(file, header=None, names=['time','timestamp','open','high','close','low','volume','change','amplitude'])

if __name__ == '__main__':
    x1 = time.time()
    # print(stochastic('4h_bitstamp.csv'))
    print(rsi('30min_bitstamp.csv','close').shape)
    # print(macd('4h_bitstamp.csv',12,26,9))
    # print(sma('4h_bitstamp.csv',50))
    # print(sma('4h_bitstamp.csv',50))
    x2 = time.time()
    print('That is the time it took to run this shit: ------------>>> ',x2-x1)
