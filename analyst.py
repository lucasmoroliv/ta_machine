import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from pprint import pprint
import json
from scipy import stats
import plotly.plotly as py

def main():
    experiment_file = 'experiment1533056746.txt'
    experiment4(experiment_file)

# --------------------------------------------------------------------------------------------------------
# * SECTION 1 *
# The seciton has functions with the goal of plotting the data in the experiment_data directory. Each one
# of them process and prints the data in a different way according to what is needed for every single analysis.

def experiment1(experiment_file):
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

def experiment2(experiment_file):
    path_experiment = 'builders/warehouse/experiment_data/' + experiment_file
    data = get_experiment(path_experiment)
    p = data['p']
    data.pop('p')
    
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
    axarr[1].set_ylabel('% of profit over {0}'.format(p['target']))
    axarr[0].set_axisbelow(True)
    axarr[0].yaxis.grid(color='gray', linestyle='dashed')
    axarr[0].xaxis.grid(color='gray', linestyle='dashed')   
    axarr[1].set_axisbelow(True)
    axarr[1].yaxis.grid(color='gray', linestyle='dashed')
    axarr[1].xaxis.grid(color='gray', linestyle='dashed')
    plt.show()

def experiment3(experiment_file):
    path_experiment = 'builders/warehouse/experiment_data/' + experiment_file
    data = get_experiment(path_experiment)
    p = data['p']    
    omega_highest = np.array(data['omega_highest'])
    omega_lowest = np.array(data['omega_lowest'])
    event_lowest = omega_lowest[omega_highest>=float(p['target'])]

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,3),(0,0),rowspan=1,colspan=1)
    ax2 = plt.subplot2grid((1,3),(0,1),rowspan=1,colspan=1,sharex=ax1,sharey=ax1)
    ax3 = plt.subplot2grid((1,3),(0,2),rowspan=1,colspan=1,sharex=ax1,sharey=ax1)
    ax1.set_ylim(-0.12, 0.12)
    ax1.hist(omega_highest,bins= 100,color='brown',orientation='horizontal')
    ax2.hist(omega_lowest,bins= 100,color='blue',orientation='horizontal')
    ax3.hist(event_lowest,bins= 100,color='red',orientation='horizontal')
    fig.subplots_adjust(wspace=0) 
    for ax in [ax2, ax3]:
        plt.setp(ax.get_yticklabels(), visible=False)
    [ax.grid() for ax in [ax1,ax2,ax3]]
    plt.yticks(np.arange(-0.12, 0.12, step=0.01))
    plt.show()

def experiment4(experiment_file):
    path_experiment = 'builders/warehouse/experiment_data/' + experiment_file
    data = get_experiment(path_experiment)
    p = data['p']    
    omega_highest = np.array(data['omega_highest'])
    omega_lowest = np.array(data['omega_lowest'])
    event_lowest = omega_lowest[omega_highest>=float(p['target'])]

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,2),(0,0),rowspan=1,colspan=1)
    ax2 = plt.subplot2grid((1,2),(0,1),rowspan=1,colspan=1,sharex=ax1,sharey=ax1)
    # I don't know why but the next line has to stay after ax1 and ax2 definition.
    plt.yticks(np.arange(-0.3, 0.3, step=0.01))
    ax1.set_ylim(-0.12,0.12)
    ax1.hist(omega_highest,bins= 500,color='brown',orientation='horizontal')
    ax2.hist(omega_lowest,bins= 500,alpha=0.5,color='blue',orientation='horizontal')
    ax2.hist(event_lowest,bins= 500,alpha=0.5,color='red',orientation='horizontal')
    fig.subplots_adjust(wspace=0) 
    plt.setp(ax2.get_yticklabels(), visible=False)
    [ax.grid() for ax in [ax1,ax2]]

    ax1.axhline(y=0.007, color='g', linestyle='-')
    ax2.axhline(y=-0.005, color='r', linestyle='-')
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








