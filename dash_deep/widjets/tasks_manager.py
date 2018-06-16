from dash_deep.app import app, task_manager 

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
from dash_deep.future import generate_table_from_future_objects

from time import sleep

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
    
            # Whenever this element is updated, it triggers
            # refresh of the table -- used in the cancel button callback
            html.Div(id='tasks-refresh-trigger')
])

@app.callback(
    Output('tasks-refresh-trigger', 'children'),
    [Input('tasks-table-cancel-button', 'n_clicks')],
     [State('tasks-data-table', 'selected_row_indices'),
      State('tasks-data-table', 'rows')])
def callback(n_clicks, selected_row_indices, rows):

    print(rows)
    print(selected_row_indices)
    
    selected_tasks_ids = map(lambda selected_row_index: rows[selected_row_index]['id'], selected_row_indices)
    
    for selected_task_id in selected_tasks_ids:
        
        task_manager.tasks_list[selected_task_id].cancel()
    
    # TODO: See if this can be done in a better way
    # Wating here for a while -- sometimes processes take
    # time to stop
    sleep(0.5)
    
    return ''


@app.callback(
    Output('tasks-data-table', 'rows'),
    [Input('tasks-table-refresh-button', 'n_clicks'),
     Input('tasks-refresh-trigger', 'children')])
def display_output(n_clicks, children):
    
    # Here we have two inputs and both can trigger this function:
    # 1) Refresh button click event.
    # 2) Update of 'tasks-refresh-trigger' element -- it is updated when
    #    cancel button is pressed.
    
    table_contents = generate_table_from_future_objects(task_manager.tasks_list) 
    
    return table_contents
