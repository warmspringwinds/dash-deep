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
    
    # Where we store the current image
    html.Div("{}", id='image-annotation-container', style={'display': 'none'}),
    
    html.Div(className='row', children=[
        html.Div(InteractiveImage('annotation-graph', image_path), className='six columns'),
    ]),
    
    # Don't need but leave it for now
    html.Pre(id='console')
])


@app.callback(Output('annotation-graph', 'figure'),
              [Input('annotation-graph', 'selectedData')],
              [State('annotation-graph', 'figure')])
def update_histogram(selectedData, figure):
    
    vertices = zip(selectedData['lassoPoints']['x'], selectedData['lassoPoints']['y'])

    path = Path( vertices )
        
    img_pil, anno_pil = trainset[0]

    img_np = np.asarray(img_pil)
    anno_np = np.asarray(anno_pil)
    
    
    height, width, _ = img_np.shape
    
    x, y = np.meshgrid( range(width), range(height-1, -1, -1))

    coors = np.hstack((x.reshape(-1, 1), y.reshape(-1,1)))

    mask = (~ path.contains_points(coors))
    mask = mask.reshape(height, width).astype(np.uint8)
    
    updated_anno = anno_np * mask
    
    #io.imsave('/home/daniil/frame005_anno.png', updated_anno)
    
    output_image = (img_np * np.expand_dims(updated_anno, 2) )
    
    final = convert_numpy_to_base64_image_string(output_image)
    
    figure['layout']['images'][0]['source'] = final
    
    
    return figure
