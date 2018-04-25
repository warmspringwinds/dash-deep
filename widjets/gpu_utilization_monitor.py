from app import app

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import os
import gpustat

# TODO: so far we just display the output of the gpustat, directly
# use the libarary and make the output look nicer


# Here we apply an interval that refreshes the state of gpu
# with a specified interval=1000ms

layout = html.Div([
   
            html.H1('GPU'),
            dcc.Interval(id='gpu-state-update-interval', interval=1000),
            html.Div(id='gpu-state-container'),
])

@app.callback(
    Output('gpu-state-container', 'children'),
    [Input('gpu-state-update-interval', 'n_intervals')])
def display_output(n):
    
    # use the gpustat pythom module to return json
    # and format into table later on
    os.system('gpustat > tmp')
    gpu_stats_string = open('tmp', 'r').read()
    
    gpu_stats_html = html.Div([  gpu_stats_string ], style={"white-space": "pre", "width": "700px"} )
    
    return gpu_stats_html
