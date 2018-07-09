import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

from dash_deep.app import app, scripts_db_models, db, task_manager

from dash_deep.widjets.widjets_factory import generate_script_inference_widjet

script_sql_class = scripts_db_models[0]

layout = generate_script_inference_widjet(script_sql_class)