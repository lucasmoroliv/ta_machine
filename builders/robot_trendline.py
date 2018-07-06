import trendline_maker
import time
from pprint import pprint

def main():
    amt_t = 4
    t_dict = t_maker(amt_t)
    key_change = {
                    'min_tests': [t_dict['t0']['min_tests'] + k for k in range(amt_t)],
                    'max_tests': [t_dict['t0']['max_tests'] + k for k in range(amt_t)]
    }
    value_changer(t_dict,amt_t,**key_change)
    automate(t_dict)

def automate(t_dict):
    for t in list(t_dict.keys()):
        try:
            trendline_maker.callable(t_dict[t])
        except:
            print('---------------------------------')
            print('No trendlines found.')
            print(t)
            print('---------------------------------')

def value_changer(t_dict,amt_t,**kwargs):
    for j in range(amt_t):
        for key in list(kwargs.keys()):
            t_dict['t{0}'.format(j)][key] = kwargs[key][j]

def t_maker(amt_t):
    t_dict = {}
    for i in range(amt_t):
        t_dict['t{0}'.format(i)] = {
            'candle_file' : '30min_1529921395_6183-2_0-40432139_bitstamp.csv',
            'timeframe' : ('2018-01-01 00:00:00','2018-06-19 23:30:00'),
            'max_span' : 100,
            'min_span' : 40,
            'upper_limit' : 0.0005,
            'lower_limit' : 0.001,
            'min_tests' :  4,
            'max_tests' : 4,
            'min_inbetween' : None
        }
        t_dict['t{0}'.format(i)]['min_inbetween'] = int(t_dict['t{0}'.format(i)]['min_span']*0.1)
    return t_dict

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
