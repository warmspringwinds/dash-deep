from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import datetime
import gpustat
import json
import os

import pkgutil
import importlib

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


# Creating database connection and initializing the database in case
# it's the first time the app is run

database_file_location = "~/.dash-deep/experiments.db"

database_file_location = os.path.expanduser( database_file_location )

database_path = os.path.dirname(database_file_location)

if not os.path.exists(database_path):
    
    os.makedirs(database_path)


server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_file_location

# Database object 
db = SQLAlchemy(server)


# In order for all our database models representing the scripts
# to be available in db object, we need to import each module representing script

# This is needed so that users can add additional scripts into scripts/ directory
# and we can automatically import all of them.
from dash_deep import scripts

for loader, name, is_pkg in pkgutil.walk_packages(scripts.__path__):
    
    full_name = scripts.__name__ + '.' + name
    
    importlib.import_module(full_name)
    
    print "Detected and registered a scipt {}\n".format(name)

    
# Now gettting all the classes representing database models of each script
# https://stackoverflow.com/questions/26514823/get-all-models-from-flask-sqlalchemy-db/26518401

scripts_db_models = [cls for cls in db.Model._decl_class_registry.values()
                     if isinstance(cls, type) and issubclass(cls, db.Model)]

# Initializing the Dash application

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