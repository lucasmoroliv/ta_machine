import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from pprint import pprint
import json
from scipy import stats
import plotly.plotly as py

def main():
    experiment_file = 'rsi_threshold1.txt'
    plot_experiment(experiment_file)

# --------------------------------------------------------------------------------------------------------
# * SECTION 1 *
# The seciton has functions with the goal of plotting the data in the experiment_data directory. Each one
# of them process and prints the data in a different way according to what is needed for every single analysis.

def plot_experiment(experiment_file):
    # It plots two graps. The first one showing the units amount and the second one the overtarget percentage,
    # both of them related to all rsi values.  
    path_experiment = 'builders/warehouse/experiment_data/' + experiment_file
    data = get_experiment(path_experiment)
    p = data['p']
    data.pop('p')
    
    [data[it].pop('unit_profit') for it in data.keys() if 'unit_profit' in data[it]]  
    experiment_list = [data[it] for it in data.keys()]
    experiment_df = pd.DataFrame(experiment_list)
    unit_amount = experiment_df['unit_amount'].values
    overtarget = experiment_df['overtarget'].values
    x = range(len(unit_amount))
    width = 1/1.5

    f, axarr = plt.subplots(2, sharex=True)
    axarr[0].bar(x, unit_amount, width, color="brown")
    axarr[1].bar(x, overtarget, width, color="blue")
    axarr[0].set_xlabel('rsi threshold')
    axarr[0].set_ylabel('Amount of units')
    axarr[1].set_xlabel('rsi threshold')
    axarr[1].set_ylabel('% of profit over 0.007')
    axarr[0].set_axisbelow(True)
    axarr[0].yaxis.grid(color='gray', linestyle='dashed')
    axarr[0].xaxis.grid(color='gray', linestyle='dashed')
    axarr[1].set_axisbelow(True)
    axarr[1].yaxis.grid(color='gray', linestyle='dashed')
    axarr[1].xaxis.grid(color='gray', linestyle='dashed')
    plt.show()

# --------------------------------------------------------------------------------------------------------
# * SECTION 2 *
# Place for random functions that may or may not be called somewhere in the code.

def get_experiment(path_experiment):
    with open(path_experiment) as f:
        data = json.load(f)
        return data

if __name__ == '__main__':
    main()








