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

import click




server = Flask(__name__)

# Creating database connection and initializing the database in case
# it's the first time the app is run

database_file_location = "~/.dash-deep/experiments.db"

database_file_location = os.path.expanduser( database_file_location )

database_path = os.path.dirname(database_file_location)

if not os.path.exists(database_path):
    
    os.makedirs(database_path)


server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database_file_location

# Uncomment this to display all sql queries that
# are being executed
#server.config['SQLALCHEMY_ECHO'] = True

# Just temporary removes warning messages
# TODO: explore more on what this option actually does
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database object 
db = SQLAlchemy(server)


# In order for all our database models representing the scripts
# to be available in db object, we need to import dash_deep.models

import dash_deep.models
    
# Now gettting all the classes representing database models of each script
# https://stackoverflow.com/questions/26514823/get-all-models-from-flask-sqlalchemy-db/26518401

scripts_db_models = [cls for cls in db.Model._decl_class_registry.values()
                     if isinstance(cls, type) and issubclass(cls, db.Model)]


# Adding default command line commands
# They are registered automatically after we import this module
import dash_deep.cli.default_commands

# Initializing the Dash application

app = dash.Dash(__name__, server=server)

from dash_deep.task import TaskManager

task_manager = TaskManager()


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