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
import copy

from PIL import Image

from dash_deep.utils import convert_numpy_to_base64_image_string, convert_base64_image_string_to_numpy
from time import sleep


sql_model = scripts_db_models[1]
trainset = sql_model.datasets['train']


def overlay_segmentation(image, segmentation):
    
    image = image.copy()
    
    if(segmentation == 1).any():
    
        blended = ( image[segmentation == 1].astype(np.float) + np.reshape(np.asarray([0, 0, 150]), (1, 3)).astype(np.float) )
        blended = (blended / blended.max()) * 255
        image[segmentation == 1] = blended.astype(np.uint8)

    if(segmentation == 2).any():
        
        blended = ( image[segmentation == 2].astype(np.float) + np.reshape(np.asarray([0, 150, 0]), (1, 3)).astype(np.float) )
        blended = (blended / blended.max()) * 255
        image[segmentation == 2] = blended.astype(np.uint8)
    
    if(segmentation == 3).any():
        
        blended = ( image[segmentation == 3].astype(np.float) + np.reshape(np.asarray([119, 255, 253]), (1, 3)).astype(np.float) )
        blended = (blended / blended.max()) * 255
        image[segmentation == 3] = blended.astype(np.uint8)
    
    return image


def check_dash_upload_contents_for_image(dash_upload_contents):
    
    if dash_upload_contents is not None:
                
        content_type, content_string = dash_upload_contents.split(',')

        if 'image' in content_type:
            
            return True
    
    return False


def create_image_graph_with_interactive_select(id_name,
                                               select_mode='select'):
    
    # select_mode='select' -- means rectangle select area
    
    # Filling the graph with default white image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[:] = 255
    height, width, _ = image.shape
    
    range_x = [0, width]
    range_y = [0, height]
    
    encoded_image = convert_numpy_to_base64_image_string(image)
    
    return dcc.Graph(
        
        id=id_name,
        
        figure={
            
            # We need a dummy data points, otherwise the lasso
            # and rectangle select area will not work
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
                'images': [{
                    'xref': 'x',
                    'yref': 'y',
                    'x': 0,
                    'y': range_y[1],
                    'sizex': range_x[1] - range_x[0],
                    'sizey': range_y[1] - range_y[0],
                    'sizing': 'stretch',
                    'layer': 'below',
                    'source': encoded_image
                }]
                ,
                'dragmode': select_mode
            }
        }
    )

def update_figure_with_new_image(figure_dict, img):
    
    height, width, _ = img.shape
    range_x = [0, width]
    range_y = [0, height]
    
    encoded_image = convert_numpy_to_base64_image_string(img)
    
    figure_dict['layout']['xaxis']['range'] = range_x
    figure_dict['layout']['yaxis']['range'] = range_y
    figure_dict['layout']['images'][0]['y'] = range_y[1]
    figure_dict['layout']['images'][0]['sizex'] = range_x[1] - range_x[0]
    figure_dict['layout']['images'][0]['sizey'] = range_y[1] - range_y[0]
    figure_dict['layout']['images'][0]['source'] = encoded_image
    
    return figure_dict

def crop_numpy_array_with_dash_rectangle_select(array_to_crop, dash_select_dict):
    
    x = dash_select_dict['range']['x']
    y = dash_select_dict['range']['y']

    x = map(lambda x_coordinate: int(round(x_coordinate)), x)
    y = map(lambda y_coordinate: int(round(y_coordinate)), y)

    # Converting the x/y coordinates into matrix
    # coordinates
    height, width = array_to_crop.shape[:2]
    y[0] = height - y[0]
    y[1] = height - y[1]

    cropped_array = array_to_crop[y[1]:y[0], x[0]:x[1]]
    
    return cropped_array




image_upload_id_name = 'image-upload'
annotation_upoad_id_name = 'annotation-upload'
sample_preview_graph_id_name = 'sample-preview-graph'
add_new_sample_button_id_name = 'add-new-sample-button'
dummy_output_id_name = 'dummy-output'
global_crop_coordinates_id_name = 'global-crop-coordinates'
crop_selection_previous_state_id_name = 'crop-selection-previous-state'
annotation_selection_previous_state_id_name = 'annotation-selection-previous-state'
annotation_dropdown_id_name = 'annotation-dropdown'
annotation_class_select_radio_id_name = 'annotation-class-select-radio'
annotation_refresh_button_id_name = 'annotation-refresh-button'
delete_sample_button_id_name = 'delete-sample-button'
annotation_graph_id_name = 'annotation-graph'
add_new_sample_button_previous_state_id_name = 'add-new-sample-previous-n-clicks'


layout = html.Div([
    html.H1("Dataset Management"),
    
    html.H3("Upload new sample"),
    
    create_image_graph_with_interactive_select(sample_preview_graph_id_name),
    
    dcc.Upload(
            id=image_upload_id_name,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select an image file')
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
    
    dcc.Upload(
            id=annotation_upoad_id_name,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select an annotation file')
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
    
    html.Button('Upload new sample',
                id=add_new_sample_button_id_name),
    
    # Below is a number of elements
    # that are meant solely to store values
    # and are not a part of UI
    html.Div(id=dummy_output_id_name,
             style={'display': 'none'}),
    html.Div(id=global_crop_coordinates_id_name,
             style={'display': 'none'}),
    html.Div(id=crop_selection_previous_state_id_name,
             style={'display': 'none'}),
    html.Div(id=annotation_selection_previous_state_id_name,
             style={'display': 'none'}),
    html.Div(id=add_new_sample_button_previous_state_id_name,
             style={'display': 'none'}),
    
    html.H3("View/Edit existing samples"),
    
    create_image_graph_with_interactive_select(annotation_graph_id_name,
                                               select_mode='lasso'),
    
    dcc.Dropdown(
                id=annotation_dropdown_id_name,
                placeholder='Select a value',
                options=[],
                multi=False
    ),
    
    dcc.RadioItems(id=annotation_class_select_radio_id_name,
                   value=0,
                   options=[
                   {'label': 'Background', 'value': 0},
                   {'label': 'Foreground', 'value': 1}
                   ]),
    
    html.Button('Refresh Table', id=annotation_refresh_button_id_name),
    
    html.Button('Delete sample',
                id=delete_sample_button_id_name)
    
])



@app.callback(Output(add_new_sample_button_previous_state_id_name, 'children'),
              [Input(add_new_sample_button_id_name, 'n_clicks')])
def callback(new_value):
    
    return new_value

# We are tracking the previous state of the selection -- here we need
# it to be able to realize which input caused the next function to be called.
# If the input argument of selection is equal to the old one, we decide
# that the call of the function was caused by another input.
@app.callback(Output(crop_selection_previous_state_id_name, 'children'),
              [Input(sample_preview_graph_id_name, 'selectedData')])
def callback(new_value):
    
    selection_json_string = json.dumps(new_value)
    
    return selection_json_string


@app.callback(Output(global_crop_coordinates_id_name, 'children'),
              [Input(sample_preview_graph_id_name, 'selectedData'),
               Input(image_upload_id_name, 'contents')],
              [State(global_crop_coordinates_id_name, 'children'),
               State(crop_selection_previous_state_id_name, 'children')])
def callback(relative_crop_coordinates,
             image_contents,
             previous_global_crop_coordinates_string,
             previous_relative_crop_coordinates_string):
    
    # If previous select region is equal to the input one,
    # then the call was cause by uploaded image -- we should reset
    # global crop coordinates (we return None)
    previous_relative_crop_coordinates = json.loads(previous_relative_crop_coordinates_string)
    
    if relative_crop_coordinates == previous_relative_crop_coordinates:
        
        return None
    
    # Checking if select was called on an image and not
    # on the empty graph object
    is_image_loaded = check_dash_upload_contents_for_image(image_contents)
    
    if not is_image_loaded:
        
        return None
    
    # It's the first select -- so the relative coordinates are
    # equal to the global ones
    if not previous_global_crop_coordinates_string:
        
        return json.dumps(relative_crop_coordinates)
    
    # Updating the global coordinates of the crop by
    # deriving the new global corrdinates updated with relative
    # selection region
    previous_global_crop_coordinates = json.loads(previous_global_crop_coordinates_string)
    
    x_global = previous_global_crop_coordinates['range']['x']
    y_global = previous_global_crop_coordinates['range']['y']
    
    x_relative = relative_crop_coordinates['range']['x']
    y_relative = relative_crop_coordinates['range']['y']
    
    x_global_updated = copy.copy( x_global )
    y_global_updated = copy.copy( y_global )
    
    x_global_updated[0] = x_global[0] + x_relative[0]
    x_global_updated[1] = x_global[0] + x_relative[1]
    
    y_global_updated[0] = y_global[0] + y_relative[0]
    y_global_updated[1] = y_global[0] + y_relative[1]
    
    global_crop_coordinates_updated = {'range':{'x':x_global_updated,
                                                'y': y_global_updated}}
    
    return json.dumps( global_crop_coordinates_updated )
    

# Callback that is responsible for deletion of a selected sample
# of the dataset.
@app.callback(Output(dummy_output_id_name, 'children'),
              [Input(delete_sample_button_id_name, 'n_clicks')],
              [State(annotation_dropdown_id_name, 'value')])
def callback(n_clicks, drop_down_value):
    
    if drop_down_value is None:
        
        return
    
    del trainset[drop_down_value]
    
    # os.remove() that is called inside of dataset
    # object sometimes takes time, so we wait to make sure
    # that files of the selected sample were actually removed.
    sleep(1)
    
    return    

# This one cleans the annotation upload container once a new image
# is loaded -- we want to erase previous annotation when we upload
# next image.
@app.callback(Output(annotation_upoad_id_name, 'contents'),
              [Input(image_upload_id_name, 'contents')])
def callback(image_contents):
              
    return None

# Callback responsible for the preview feature -- 
# display uploaded image and annotation and show the preview.
# If no annotation was uploaded we initialize an empty one.
@app.callback(Output(sample_preview_graph_id_name, 'figure'),
              [Input(image_upload_id_name, 'contents'),
               Input(annotation_upoad_id_name, 'contents'),
               Input(global_crop_coordinates_id_name, 'children')],
              [State(sample_preview_graph_id_name, 'figure')])
def callback(image_contents,
             annotation_contents,
             global_crop_coordinates_string,
             figure):
    
    
    is_image_loaded = check_dash_upload_contents_for_image(image_contents)
    is_annotation_loaded = check_dash_upload_contents_for_image(annotation_contents)
    
    if not is_image_loaded:
        
        return figure
    
    image_np = convert_base64_image_string_to_numpy(image_contents)
    output_image = image_np
    
    if is_annotation_loaded:
                
        annotation_np = convert_base64_image_string_to_numpy(annotation_contents)
        output_image = overlay_segmentation(image_np, annotation_np)
    
    if global_crop_coordinates_string:
        
        global_crop_coordinates = json.loads(global_crop_coordinates_string)
        
        output_image = crop_numpy_array_with_dash_rectangle_select(output_image,
                                                                   global_crop_coordinates)

    output_figure = update_figure_with_new_image(figure, output_image)
    
    return output_figure

# Callback responsible for an addition of a new sample
# into the selected dataset. It also automatically opens
# up the added sample in the viewer.
@app.callback(Output(annotation_dropdown_id_name, 'value'),
              [Input(add_new_sample_button_id_name, 'n_clicks'),
               Input(delete_sample_button_id_name, 'n_clicks')],
              [State(image_upload_id_name, 'contents'),
               State(annotation_upoad_id_name, 'contents'),
               State(annotation_dropdown_id_name, 'value'),
               State(global_crop_coordinates_id_name, 'children'),
               State(add_new_sample_button_previous_state_id_name, 'children')])
def callback(add_button_n_clicks,
             delete_button_n_clicks,
             image_contents,
             annotation_contents,
             dropdown_previous_selection,
             global_crop_coordinates_string,
             old_number_of_add_button_clicks_string):
    
    if add_button_n_clicks == old_number_of_add_button_clicks_string:
        
        return -1
        
    is_image_loaded = check_dash_upload_contents_for_image(image_contents)
    is_annotation_loaded = check_dash_upload_contents_for_image(annotation_contents)
    
    if not is_image_loaded:
        
        return dropdown_previous_selection
    
    image_np = convert_base64_image_string_to_numpy(image_contents)
    annotation_np = np.zeros((image_np.shape[0], image_np.shape[1]),
                             dtype=np.uint8)
    
    if is_annotation_loaded:
            
        annotation_np = convert_base64_image_string_to_numpy(annotation_contents)
    
    if global_crop_coordinates_string:
        
        global_crop_coordinates = json.loads(global_crop_coordinates_string)
        
        image_np = crop_numpy_array_with_dash_rectangle_select(image_np, global_crop_coordinates)
        annotation_np = crop_numpy_array_with_dash_rectangle_select(annotation_np, global_crop_coordinates)
    
    image_pil = Image.fromarray(image_np)
    annotation_pil = Image.fromarray(annotation_np)
    
    index = trainset.add_new_sample((image_pil, annotation_pil))
        
    return index

# Callback that is responsible for refreshing of the samples
# id list after addition/deletion/refresh buttons.
@app.callback(Output(annotation_dropdown_id_name, 'options'),
              [Input(annotation_refresh_button_id_name, 'n_clicks'),
               Input(add_new_sample_button_id_name, 'n_clicks'),
               Input(delete_sample_button_id_name, 'n_clicks')])
def callback(n_clicks, n_clicks_1, n_clicks_2):
    
    # Small hack: since this function is called
    # at the same time as the function responsible for
    # addition of a new sample -- we need to wait until
    # the sample will be uploaded and then render the updated
    # sample list.
    sleep(1.5)

    number_of_records = len(trainset)
    
    print(number_of_records)
    
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
@app.callback(Output(annotation_selection_previous_state_id_name, 'children'),
              [Input(annotation_graph_id_name, 'selectedData')])
def callback(new_value):
    
    selection_json_string = json.dumps(new_value)
    
    return selection_json_string

# Core callback that is responsible for annotation of selected sample.
# It loads the image and annotation file from the dataset, updates
# annotation with the region specified by the user and commits those changes
# onto the disk.
@app.callback(Output(annotation_graph_id_name, 'figure'),
              [Input(annotation_graph_id_name, 'selectedData'),
               Input(annotation_dropdown_id_name, 'value')],
              [State(annotation_graph_id_name, 'figure'),
               State(annotation_selection_previous_state_id_name, 'children'),
               State(annotation_class_select_radio_id_name, 'value')])
def update_histogram(selected_data,
                     drop_down_value,
                     figure,
                     previous_selected_data_string,
                     class_select_mode):
    
    if drop_down_value == -1:
        
        output_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        return update_figure_with_new_image(figure, output_image)
    
    img_pil, anno_pil = trainset[drop_down_value]

    img_np = np.asarray(img_pil)
    anno_np = np.asarray(anno_pil)
    
    previous_selected_data = json.loads(previous_selected_data_string)
    
    if previous_selected_data != selected_data:
        
        vertices = zip(selected_data['lassoPoints']['x'],
                       selected_data['lassoPoints']['y'])

        path = Path( vertices )

        height, width, _ = img_np.shape

        x, y = np.meshgrid( range(width), range(height-1, -1, -1))

        coors = np.hstack((x.reshape(-1, 1), y.reshape(-1,1)))

        mask = path.contains_points(coors).reshape(height, width)
        
        anno_np = anno_np.copy()
        anno_np[mask] = class_select_mode
        
        trainset[drop_down_value] = Image.fromarray(anno_np)
    
    
    output_image = overlay_segmentation(img_np, anno_np)
    
    new_figure = update_figure_with_new_image(figure, output_image)
    
    return new_figure
