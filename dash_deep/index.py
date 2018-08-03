from dash_deep.app import app, scripts_db_models, server, task_manager

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table_experiments import DataTable

from dash_deep.widjets import gpu_utilization_monitor
from dash_deep.widjets import tasks_manager

from dash_deep.utils import generate_scripts_widjets_and_cli_interfaces


index_page, scripts_full_url_widjet_look_up_table, scripts_name_and_cli_instance_pairs = generate_scripts_widjets_and_cli_interfaces(scripts_db_models)


for script_cli_name, script_cli_interface in scripts_name_and_cli_instance_pairs:
    
    server.cli.add_command(script_cli_interface, name=script_cli_name)

    
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),#, style={ 'border': '1px solid #d6d6d6', 'padding': '44px'}),
    
    # Fix for:https://community.plot.ly/t/data-tables-with-multi-pages/7282
    html.Div(DataTable(rows=[{}]), style={'display': 'none'})
], className='container', style={'text-align': 'center'})



# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    
    # TODO: refactor this part into a special router object
    # will be much cleaner
    
    if pathname == '/gpu':
        
        return gpu_utilization_monitor.layout
    
    elif pathname == '/tasks':
        
        return tasks_manager.layout
    
    elif pathname in scripts_full_url_widjet_look_up_table:
        
        return scripts_full_url_widjet_look_up_table[ pathname ]
    
    else:
        
        return index_page

# TODO: for some reason the server crushes when being run
# in a debug mode.
    
if __name__ == '__main__':
    
    # Read dash_deep/task.py for more info about this
    # piece of code.
    try:
        server.cli()
        
    except (Exception, KeyboardInterrupt) as e:
   
        print(e.message)
        
    finally:
        
        task_manager.shutdown()
    
    