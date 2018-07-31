import pandas as pd 
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.offline as offline
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from pprint import pprint

def main():
    # candle0_time = '2014-01-04 00:00:00'
    # candle0_ts = calendar.timegm(time.strptime(candle0_time, '%Y-%m-%d %H:%M:%S'))
    candle0_ts = '1523854800'
    candles = ['0','5']
    callable(candle0_ts,candles)

def callable(candles0_ts,candles):

    path_candle_file = 'builders/warehouse/candle_data/' + '30min_bitstamp.csv'
    pre_df = get_dataframe(path_candle_file)
    
    start_index = pre_df.index[pre_df['timestamp']==int(candles0_ts)][0]
    end_index = start_index + int(candles[1])

    df = pre_df[start_index:end_index+1]
    
    # INITIAL CANDLESTICK

    INCREASING_COLOR = '#32CD32'
    DECREASING_COLOR = '#FF0000'

    data = [ dict(
        type = 'candlestick',
        open = df.open,
        high = df.high,
        low = df.low,
        close = df.close,
        x = df.time,
        yaxis = 'y2',
        name = 'GS',
        increasing = dict( line = dict( color = INCREASING_COLOR ) ),
        decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
    ) ]

    layout=dict()

    fig = dict( data=data, layout=layout )

    # CREATE THE LAYOUT OBJECT

    fig['layout'] = dict()
    fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
    fig['layout']['xaxis'] = dict( rangeselector = dict( visible = True ) )
    fig['layout']['yaxis'] = dict( domain = [0, 0.2], showticklabels = False )
    fig['layout']['yaxis2'] = dict( domain = [0.2, 0.8] )
    fig['layout']['legend'] = dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom' )
    fig['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )

    # ADD RANGE BUTTONS

    rangeselector=dict(
        visibe = True,
        x = 0, y = 0.9,
        bgcolor = 'rgba(150, 200, 250, 0.4)',
        font = dict( size = 13 ),
        buttons=list([
            dict(count=1,
                label='reset',
                step='all'),
            dict(count=1,
                label='1yr',
                step='year',
                stepmode='backward'),
            dict(count=3,
                label='3 mo',
                step='month',
                stepmode='backward'),
            dict(count=1,
                label='1 mo',
                step='month',
                stepmode='backward'),
            dict(step='all')
        ]))
    
    fig['layout']['xaxis']['rangeselector'] = rangeselector

    # PLOT

    plot( fig, filename = 'candlestick-test-3', validate = False)  

def get_dataframe(df_file):
    return pd.read_csv(df_file, header=None, names=['time','timestamp','open','high','low','close','volume','change'])

if __name__ == '__main__':
    main()


