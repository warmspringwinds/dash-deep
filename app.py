from flask import Flask
import dash
from dash.dependencies import Input, Output, State
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

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})