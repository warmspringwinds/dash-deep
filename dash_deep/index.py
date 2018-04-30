from dash_deep.app import app, scripts_db_models, server

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from dash_deep.widjets import gpu_utilization_monitor
from dash_deep.widjets import training_jobs_monitor
from dash_deep.widjets import widjets_factory

from dash_deep.utils import get_script_titles_and_url_endpoints
from dash_deep.utils import generate_wtform_classes_and_input_form_widjets


script_files_title_names, script_files_url_endpoints = get_script_titles_and_url_endpoints(scripts_db_models)

main_page_scripts_widjet_layout = widjets_factory.generate_main_page_scripts_widjet(script_files_title_names, script_files_url_endpoints)

wtform_classes, scripts_input_form_widjets = generate_wtform_classes_and_input_form_widjets(scripts_db_models)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


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
        
        return training_jobs_monitor.layout
    
    elif pathname == '/scripts':
        
        return main_page_scripts_widjet_layout
    
    elif pathname in script_files_url_endpoints:
        
        return scripts_input_form_widjets[ script_files_url_endpoints.index(pathname) ]
    
    else:
        
        return index_page

    
if __name__ == '__main__':
    
    server.run(host='0.0.0.0')
    