from app import *

import widjets.gpu_utilization_monitor
import widjets.training_jobs_monitor


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



script_parse_layout = html.Div([

    html.Label('Scipt to parse'),
    dcc.Input(id='input-1'),

    html.Button('Parse script', id='button-2'),

    html.Div(id='output')
    
], className='container')



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
    
    if pathname == '/gpu':
        
        return widjets.gpu_utilization_monitor.layout
    
    elif pathname == '/tasks':
        
        return widjets.training_jobs_monitor.layout
    
    elif pathname == '/scripts':
        
        return script_parse_layout
    
    else:
        
        return index_page

    
if __name__ == '__main__':
    
    server.run(host='0.0.0.0')
    