from dash_deep.app import app, scripts_db_models

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from dash_deep.widjets.widjets_factory import generate_dataset_management_widjet

#sql_model = scripts_db_models[1]

layouts = []

for script_db_model in scripts_db_models:
    
    layouts.append(generate_dataset_management_widjet(script_db_model))
    

layout = layouts[0]