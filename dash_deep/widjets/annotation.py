from dash_deep.app import app, scripts_db_models

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import base64
import json
import skimage.io as io

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

import numpy as np
import json

from dash_deep.utils import convert_numpy_to_base64_image_string, convert_base64_image_string_to_numpy

sql_model = scripts_db_models[0]

trainset = sql_model.datasets['train']

RANGE = [0, 1]

def InteractiveImage(id, image_path):
    
    encoded_image = base64.b64encode(open(image_path, 'rb').read())
    
    img = io.imread(image_path)
    height, width, _ = img.shape
    
    range_x = [0, width]
    range_y = [0, height]
    
    return dcc.Graph(
        id=id,
        figure={
            # We need a dummy data points, otherwise the lasso
            # won't work
            'data': [{'x': [0.5], 'y': [0.5] }],
            'layout': {
                'xaxis': {
                    'range': range_x
                },
                'yaxis': {
                    'range': range_y,
                    'scaleanchor': 'x',
                    'scaleratio': 1
                },
                'height': 600,
                'images': [{
                    'xref': 'x',
                    'yref': 'y',
                    'x': 0,
                    'y': range_y[1],
                    'sizex': range_x[1] - range_x[0],
                    'sizey': range_y[1] - range_y[0],
                    'sizing': 'stretch',
                    'layer': 'below',
                    'source': 'data:image/png;base64,{}'.format(encoded_image)
                }]
                ,
                'dragmode': 'lasso'  # or 'lasso'
            }
        }
    )

image_path = '/home/daniil/frame005.png'
annotation_path = '/home/daniil/frame005_anno.png'


layout = html.Div([
    
    dcc.Upload(
            id='image-upload',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            }
        ),
    
    
    html.Div(id='annotation-selection-previous-state', style={'display': 'none'}),
    
    
    dcc.Dropdown(
                id='annotation-dropdown',
                placeholder='Select a value',
                options=[],
                multi=False
    ),
    
    html.Button('Refresh Table', id='annotation-button'),
    
    html.Div(className='row', children=[
        html.Div(InteractiveImage('annotation-graph', image_path), className='six columns'),
    ]),
    
])



@app.callback(Output('annotation-dropdown', 'options'),
              [Input('annotation-button', 'n_clicks')])
def callback(n_clicks):

    number_of_records = len(trainset)
    
    table = []

    for i in xrange(number_of_records):
        
        table.append({'label':'Sample #{}'.format(i), 'value': i})

    return table


# We are tracking the previous state of the selection -- this is needed
# to prevent an update that might be caused when we switch to a new
# dataset sample but the selection values are still there -- that might
# cause the update of a sample even though user never applied it to the
# new image. So, if the selection is old, we don't perform an update on the
# dataset
@app.callback(Output('annotation-selection-previous-state', 'children'),
              [Input('annotation-graph', 'selectedData')])
def callback(new_value):
    
    selection_json_string = json.dumps(new_value)
    
    return selection_json_string 


@app.callback(Output('annotation-graph', 'figure'),
              [Input('annotation-graph', 'selectedData'),
               Input('annotation-dropdown', 'value')],
              [State('annotation-graph', 'figure'),
               State('annotation-selection-previous-state', 'children')])
def update_histogram(selectedData, value, figure, previous_selected_data_string):
    
    
    img_pil, anno_pil = trainset[value]

    img_np = np.asarray(img_pil)
    anno_np = np.asarray(anno_pil)
    
    previous_selected_data = json.loads(previous_selected_data_string)
    
    if previous_selected_data != selectedData:
        
        vertices = zip(selectedData['lassoPoints']['x'],
                       selectedData['lassoPoints']['y'])

        path = Path( vertices )

        height, width, _ = img_np.shape

        x, y = np.meshgrid( range(width), range(height-1, -1, -1))

        coors = np.hstack((x.reshape(-1, 1), y.reshape(-1,1)))

        mask = (~ path.contains_points(coors))
        mask = mask.reshape(height, width).astype(np.uint8)

        anno_np = anno_np * mask
    
    # Convert the mask to one hot mask
    
    # update the respective one hot of a certain class
    
    # use __set_item__ to save the changes
    
    #io.imsave('/home/daniil/frame005_anno.png', updated_anno)
    
    output_image = (img_np * np.expand_dims(anno_np, 2) )
    
    final = convert_numpy_to_base64_image_string(output_image)
    
    figure['layout']['images'][0]['source'] = final
    
    
    return figure
