from flask import Flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import datetime
import gpustat
import json
import os

from pebble import ProcessPool
from time import sleep
from multiprocessing import Manager

import random


tasks = []
losses_arrays = []

process_pool = ProcessPool()

# We use manager to perform the communication between processes
manager = Manager()


def slow_function(process_list):
    
    for x in xrange(3):
        
        sleep(3)
        process_list.append(random.random())
        
    return


server = Flask(__name__)

app = dash.Dash(__name__, server=server)

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div([
    dcc.Link('GPU utilization', href='/gpu'),
    html.Br(),
    dcc.Link('Tasks tracking', href='/tasks'),
])


page_1_layout = html.Div([
    html.H1('GPU'),
    dcc.Interval(id='gpu-state-update-interval', interval=1000),
    html.Div(id='my-output-interval'),
])


tasks_page_layout = html.Div([
    html.H1('Tasks Management'),
    
    html.Button('Create a new task', id='button'),
    html.H3(id='button-clicks'),
    
    html.H1('Active Tasks'),
    dcc.Interval(id='active-tasks-state-update-interval', interval=1000),
    html.Div(id='active-tasks-output-interval'),
    dcc.Graph(
        id='graph-1',
        figure={
            'data': [{
                'y': [1, 4, 3]
            }],
           'layout': {
               'height': 800
           }
        }
    ),
])


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def clicks(n_clicks):
    
    #if n_clicks == 1:
    #    return "pressed"
    
    process_list = manager.list([])

    losses_arrays.append(process_list)
    
    future = process_pool.schedule(slow_function, args=[process_list])
    tasks.append(future)
    
    return "pressed"


@app.callback(
    Output('my-output-interval', 'children'),
    [Input('gpu-state-update-interval', 'n_intervals')])
def display_output(n):
    
    # use the gpustat pythom modul to return json
    # and format into table later on
    os.system('gpustat > tmp')
    gpu_stats_string = open('tmp', 'r').read()
    
    gpu_stats_html = html.Div([  gpu_stats_string ], style={"white-space": "pre", "width": "700px"} )
    
    return gpu_stats_html


@app.callback(
    Output('graph-1', 'figure'),
    [Input('active-tasks-state-update-interval', 'n_intervals')])
def display_output(n):
    
    
    losses = map(lambda arr: {'y':list(arr)}, losses_arrays)
    
    fig = {'data': losses}
    
    return fig


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    
    if pathname == '/gpu':
        
        return page_1_layout
    
    elif pathname == '/tasks':
        
        return tasks_page_layout
    else:
        
        return index_page