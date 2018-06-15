from dash_deep.app import app, task_manager 

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
from dash_deep.future import generate_table_from_future_objects

layout = html.Div([
    
            html.H1('Tasks Management'),
            dt.DataTable(
                         rows=[{}],
                         id='tasks-data-table',
                         row_selectable=True,
                         filterable=True,
                         ),
            html.Button('Refresh Table', id='tasks-table-refresh-button'),
            html.Button('Cancel/Delete', id='tasks-table-cancel-button'),
            html.Div(id='tasks-table-dummy-output')
])

@app.callback(
    Output('tasks-table-dummy-output', 'children'),
    [Input('tasks-table-cancel-button', 'n_clicks')],
     [State('tasks-data-table', 'selected_row_indices'),
      State('tasks-data-table', 'rows')])
def callback(n_clicks, selected_row_indices, rows):

    print(rows)
    print(selected_row_indices)
    
    selected_tasks_ids = map(lambda selected_row_index: rows[selected_row_index]['id'], selected_row_indices)
    
    for selected_task_id in selected_tasks_ids:
        
        task_manager.tasks_list[selected_task_id].cancel()
        

    return ''


@app.callback(
    Output('tasks-data-table', 'rows'),
    [Input('tasks-table-refresh-button', 'n_clicks')])
def display_output(n_clicks):
    
    table_contents = generate_table_from_future_objects(task_manager.tasks_list) 
    
    return table_contents
