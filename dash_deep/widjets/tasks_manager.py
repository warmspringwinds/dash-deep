from dash_deep.app import app, task_manager 

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

layout = html.Div([
    
            html.H1('Tasks Management'),

            html.H1('Active Tasks'),
    
            dcc.Interval(id='active-tasks-state-update-interval', interval=1000),
            html.Div(id='active-tasks-output-interval'),
])



@app.callback(
    Output('active-tasks-output-interval', 'children'),
    [Input('active-tasks-state-update-interval', 'n_intervals')])
def display_output(n):
    
    return str(task_manager.tasks_list)
