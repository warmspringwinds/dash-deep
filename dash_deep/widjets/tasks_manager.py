from dash_deep.app import app, task_manager 

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table_experiments as dt
from dash_deep.future import generate_table_from_future_objects

layout = html.Div([
    
            html.H1('Tasks Management'),

            html.H1('Active Tasks'),
            dt.DataTable(
                         rows=[{}],
                         id='tasks-data-table',
                         row_selectable=True,
                         filterable=True,
                         ),
            html.Button('Refresh Table', id='tasks-table-refresh-button')
])


@app.callback(
    Output('tasks-data-table', 'rows'),
    [Input('tasks-table-refresh-button', 'n_clicks')])
def display_output(n_clicks):
    
    table_contents = generate_table_from_future_objects(task_manager.tasks_list) 
    
    return table_contents
