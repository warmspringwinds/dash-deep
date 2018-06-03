from dash_deep.app import app, scripts_db_models, server, task_manager

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from dash_deep.widjets import gpu_utilization_monitor
#from dash_deep.widjets import training_jobs_monitor
from dash_deep.widjets import widjets_factory
from dash_deep.widjets import tasks_manager

from dash_deep.utils import get_script_titles_url_endpoints_and_cli_names
from dash_deep.utils import generate_wtform_instances_and_input_form_widjets, generate_scripts_input_form_cli_interfaces


script_files_title_names, script_files_url_endpoints, cli_names = get_script_titles_url_endpoints_and_cli_names(scripts_db_models)

main_page_scripts_widjet_layout = widjets_factory.generate_main_page_scripts_widjet(script_files_title_names, script_files_url_endpoints)

wtform_classes, scripts_input_form_widjets = generate_wtform_instances_and_input_form_widjets(scripts_db_models)

scripts_input_form_cli_interfaces = generate_scripts_input_form_cli_interfaces(wtform_classes)

# TODO: factor out into a separate function?
# Names are not defined so we get an empty strings in our command line
# we should somehow push names there.

for script_number, scripts_input_form_cli_interface in enumerate(scripts_input_form_cli_interfaces):
    
    server.cli.add_command( scripts_input_form_cli_interface,
                           name=cli_names[script_number] )
    
    
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], className='container')


index_page = html.Div([
    dcc.Link('GPU utilization', href='/gpu'),
    html.Br(),
    dcc.Link('Tasks tracking', href='/tasks'),
    html.Br(),
    dcc.Link('Training script parsing', href='/scripts')
])




@app.callback(
    Output('output', 'children'),
    [Input('button-2', 'n_clicks')],
    state=[State('input-1', 'value')])
def compute(n_clicks, input1):
    return 'A file to parse {}'.format(
        input1
    )


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    
    # TODO: refactor this part into a special router object
    # will be much cleaner
    
    if pathname == '/gpu':
        
        return gpu_utilization_monitor.layout
    
    elif pathname == '/tasks':
        
        #return training_jobs_monitor.layout
        return tasks_manager.layout
    
    elif pathname == '/scripts':
        
        return main_page_scripts_widjet_layout
    
    elif pathname in script_files_url_endpoints:
        
        return scripts_input_form_widjets[ script_files_url_endpoints.index(pathname) ]
    
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
    
    