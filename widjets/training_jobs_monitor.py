from app import manager, losses_arrays, process_pool, tasks, app, slow_function


import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# Here we have a button that creates a separate process that generates random numbers and
# updates the list with loss which is shared between all processes

# We have an interval event that periodically updates the state of each process

layout = html.Div([
    
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
            )
])


@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def clicks(n_clicks):
    
    # TODO: for some reason the pressed button event is triggered one we land
    # the page -- correct that
    
    #if n_clicks == 1:
    #    return "pressed"
    
    process_list = manager.list([])

    losses_arrays.append(process_list)
    
    future = process_pool.schedule(slow_function, args=[process_list])
    tasks.append(future)
    
    return "pressed"



@app.callback(
    Output('graph-1', 'figure'),
    [Input('active-tasks-state-update-interval', 'n_intervals')])
def display_output(n):
    
    
    losses = map(lambda arr: {'y':list(arr)}, losses_arrays)
    
    fig = {'data': losses}
    
    return fig
