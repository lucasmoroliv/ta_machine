import pandas as pd
import time, datetime, sys, csv
import numpy as np
from pprint import pprint
import json

def callable():
    df_file = '30min_bitstamp.csv'
    df = get_dataframe('warehouse/candle_data/' + df_file)
    df, highest, lowest = td_setup(df,df_file)
    return td_countdown(df, highest, lowest)

def main():
    df_file = '30min_bitstamp.csv'
    df = get_dataframe('warehouse/candle_data/' + df_file)
    df, highest, lowest = td_setup(df,df_file)
    td_countdown(df, df_file, highest, lowest)

def get_dataframe(df_file):
  return pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])

def td_setup(df,df_file):
    # First we add a column into the dataframe, a column with the close value 4 candles before the current candle.
    df = df[['timestamp','close','low','high']].copy()
    df['dif_4th'] = list(pd.Series(df.loc[:3, 'close']))+list(df.loc[:df.shape[0]-5, 'close'])
    df['dif_4th'] = list(df.loc[:3, 'close'])+list(df.loc[:df.shape[0]-5, 'close'])
    # Here we add a colum(named: delta) which is the subtraction between the current close price and close price 4 candles before
    df['delta'] = df['close'] - df['dif_4th']
#     # How TD Setup works in a Bear Market:
#     # TD Buy Setup, The buy setup bar 1 starts to count when the close of the current bar is lower than the close four bars earlier,
#     # the 2 counts if the bar next to the 1 closes lower than the close four bars earlier, and so on... The count needs to be back to back.
#     # The Minimal Buy Setup (min_buy_setup): If we reach bar8 8, to be classified as a minimal buy setup, the low of bar 8 has to be equal
#     # or lower to the low of bars 6 and 7. Otherwise it will be just a normal 8.
#     # THe Perfect Buy Setup (perfect_buy_setup): If we reach bar 9, the td buy setup is perfected if either bar 9 and 8's low is equal or
#     # lower than the lows of bars 6 and 7self
#     ## OBS: The TD Sell Setup works exactly with the oposite assumptions from the bear market to the bull market.
#     ### Here with a couple of conditional statements all the conditions regarding the bear and bull market, to make a new column(named: td),
#     ### wich is the td of the candle.
    count = 0
    tdlist = []
    highest = []
    lowest = []
    min_buy_setup = -80
    perfect_buy_setup = -90
    min_sell_setup = 80
    perfect_sell_setup = 90
    for i in range(df.shape[0]):
        if df.delta[i] < 0 and count >= 0:
            count = -1
            tdlist.append(count)
        elif df.delta[i] <= 0 and count > -9 and count < 0:
            if count == -7 and df.low[i] <= min(df.low[i-1], df.low[i-2]):
                count -= 1
                tdlist.append(min_buy_setup)
            elif count == -8 and max(df.low[i],df.low[i-1]) <= min(df.low[i-2], df.low[i-3]):
                count -= 1
                tdlist.append(perfect_buy_setup)
                highest.append(i-8)
            else:
                count -= 1
                tdlist.append(count)
                if count == -9:
                    highest.append(i-8)
        elif df.delta[i] <= 0 and count == -9:
            count = -1
            tdlist.append(count)
        elif df.delta[i] > 0 and count <= 0:
            count = 1
            tdlist.append(count)
        elif df.delta[i] >= 0 and count < 9 and count > 0:
            if count == 7 and df.high[i] > max(df.high[i-1], df.high[i-2]):
                count += 1
                tdlist.append(min_sell_setup)
            elif count == 8 and min(df.high[i], df.high[i-1]) >= max(df.high[i-2], df.high[i-3]):
                count += 1
                tdlist.append(perfect_sell_setup)
                lowest.append(i-8)
            else:
                count += 1
                tdlist.append(count)
                if count == 9:
                    lowest.append(i-8)
        elif df.delta[i] >= 0 and count == 9:
            count = 1
            tdlist.append(count)
        else:
            count = 0
            tdlist.append(count)
    df['td'] = tdlist
    td_s_array = np.zeros([df.shape[0],2])
    td_s_array[:,0] = df['timestamp']
    td_s_array[:,1] = df['td']
    td_s_array = td_s_array.astype(int)

    path_data_object = 'warehouse/td_data/' + 'td_setup_' + df_file.split('_')[0] + '_bitstamp.csv'
    with open(path_data_object, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(td_s_array.shape[0]):
            spamwriter.writerow([td_s_array[i,0],td_s_array[i,1]])
    return df, highest, lowest

def td_countdown(df, df_file, highest, lowest):
    # How Td Buy Countdown works in a bear market:
    # Starts after the finish of a buy setup. The close of bar 9 should be less than the low two bars earlier. If satisfied bar 9 of the setup,
    # becomer bar 1 of the countdwn. If the conditions is not met, then bar 1 of the countdown is postponed until the conditions is satisfied
    # and you continue to count until there are a total of thirthen closes, each one less than, or equal to the low two bars earlier.
    ## OBS: The Td Buy Countdown might be cancelled under these two conditions:
    ## 1 - If a Td Sell Setup completes before recording a 13 count, then TD Buy Countdown is cancelled.
    ## 2 - If a price bar records a low that is higher than the highest high of the recent Td Buy Setup.

    # We add a column into the dataframe, a column with the low value 2 candles before the current candle.
    df['dif_2th_neg'] = list(df.loc[:1, 'low'])+list(df.loc[:df.shape[0]-3, 'low'])
    # We add a column into the dataframe, a column with the high value 2 candles before the current candle.
    df['dif_2th_pos'] = list(df.loc[:1, 'high'])+list(df.loc[:df.shape[0]-3, 'high'])

    # Here we add a colum(named: dota) which is the subtraction between the current close price and the low price 2 candles earlier
    df['dota'] = df['close'] - df['dif_2th_neg']

    # Here we add a colum(named: deltb) which is the subtraction between the current close price and the high price 2 candles earlier
    df['deltb'] = df['close'] - df['dif_2th_pos']

    countdown = []
    indexes_full_setup = []
    counter = 0 # is used to put the number in those candles which fit in the countdown requirements
    trigger = 0 # if the bar 9 of the setup is not the 1 of the countdown at the same time, trigger activate the number 1 of the countdown, when the close of the current candle is lower than the low two candles earlier(for td_buy_countdown)
    n = np.nan # all those candles that doens't receive any countdown number are NaN.
    aaa = 0 # In the middle of a countdown a cancel might happen and the count start over, if 0 appears is because one of the cancelattion conditions is contemplated
    for i in range(df.shape[0]):
        if df.dota[i] <= 0 and counter == 0 and df.td[i] == -9:
            counter = -1
            countdown.append(counter)
        elif df.dota[i] <= 0 and counter == 0 and df.td[i] == -90:
            counter = -1
            countdown.append(counter)
        elif df.dota[i] > 0 and counter == 0 and df.td[i] == -9:
            counter = 0
            countdown.append(counter)
            trigger = -1
        elif df.dota[i] > 0 and counter == 0 and df.td[i] == -90:
            counter = 0
            countdown.append(counter)
            trigger = -1
        elif counter < 0 and counter > -13 and df.td[i] == 9:
            counter = 0
            countdown.append(aaa)
            trigger = 0
        elif counter < 0 and counter > -13 and df.td[i] == 90:
            counter = 0
            countdown.append(aaa)
            trigger = 0
        elif df.dota[i] < 0 and counter < 0 and counter > -13:
            counter -= 1
            countdown.append(counter)
        elif df.dota[i] < 0 and trigger == -1 and counter > -13:
            counter -= 1
            countdown.append(counter)
        elif counter < 0 and counter > -13:
            list_of_potential_setups = [r for r in highest if i-r>0]
            maxim = max(list_of_potential_setups) #maxim é o index 1 do buy setup correspondente ao countdown atual
            for t in range(9):
                indexes_full_setup.append(maxim+t)
                max_high = 0
            for u in indexes_full_setup:
                if df.high[u] > max_high:
                    max_high = df.high[u]
            indexes_full_setup = []
            if df.low[i] > max_high:
                counter = 0
                countdown.append(aaa)
                trigger = 0
            else:
                countdown.append(n)
        elif df.dota[i] < 0 and counter == -13:
            counter = 0
            countdown.append(n)
            trigger = 0
        elif df.deltb[i] >= 0 and counter == 0 and df.td[i] == 9:
            counter = 1
            countdown.append(counter)
        elif df.deltb[i] >= 0 and counter == 0 and df.td[i] == 90:
            counter = 1
            countdown.append(counter)
        elif df.deltb[i] < 0 and counter == 0 and df.td[i] == 9:
            counter = 0
            countdown.append(counter)
            trigger = 1
        elif df.deltb[i] < 0 and counter == 0 and df.td[i] == 90:
            counter = 0
            countdown.append(counter)
            trigger = 1
        elif counter > 0 and counter < 13 and df.td[i] == -9:
            counter = 0
            countdown.append(aaa)
            trigger = 0
        elif counter > 0 and counter < 13 and df.td[i] == -90:
            counter = 0
            countdown.append(aaa)
            trigger = 0
        elif df.deltb[i] > 0 and counter > 0 and counter < 13:
            counter += 1
            countdown.append(counter)
        elif df.deltb[i] > 0 and trigger == 1 and counter < 13:
            counter += 1
            countdown.append(counter)
        elif counter > 0 and counter < 13:
            list_of_potential_setups = [r for r in lowest if i-r>0]
            minim = max(list_of_potential_setups) #minim é o index 1 do buy setup correspondente ao countdown atual
            for t in range(9):
                indexes_full_setup.append(minim+t)
                min_high = 1000000000
            for u in indexes_full_setup:
                if df.low[u] < min_high:
                    min_high = df.low[u]
            indexes_full_setup = []
            if df.high[i] < min_high:
                counter = 0
                countdown.append(aaa)
                trigger = 0
            else:
                countdown.append(n)
        elif df.deltb[i] > 0 and counter == 13:
            counter = 0
            countdown.append(n)
            trigger = 0
        else:
            countdown.append(n)
    df['countdown'] = countdown
    td_c_array = np.zeros([df.shape[0],2])
    td_c_array[:,0] = df['timestamp']
    td_c_array[:,1] = df['countdown']
    td_c_array = td_c_array.astype(int)

    path_data_object = 'warehouse/td_data/' + 'td_countdown_' + df_file.split('_')[0] + '_bitstamp.csv'
    with open(path_data_object, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(td_c_array.shape[0]):
            spamwriter.writerow([td_c_array[i,0],td_c_array[i,1]])
    ## These lines are here for tests, we can check the amounts of ZERAR, 13, -13, 12, 9, etc...
    # for index, row in df.iterrows():
    #     if df.countdown[index] == 'ZERAR':
    #         print(index)
    # print('')
    # for index, row in df.iterrows():
    #     if df.countdown[index] == 13:
    #         print(index)
    # print('')

if __name__ == '__main__':
    x1 = time.time()
    main()
    x2 = time.time()
    print('TIme to run: --->>> ',x2-x1)
