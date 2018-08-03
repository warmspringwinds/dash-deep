import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

from dash_deep.app import app, task_manager
from dash_deep.sql import (get_column_names_and_values_from_sql_model_instance,
                           get_column_names_from_sql_model_class,
                           generate_script_wtform_class_instance)

from dash_deep.app import db
import dash_table_experiments as dt
from dash_deep.plot import create_mutual_plot
from dash_deep.sql import generate_table_contents_from_sql_model_class

# Temporary solution for the problem of circular imports
import dash_deep.utils

import json
import copy
import numpy as np
from time import sleep

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from PIL import Image



def generate_script_navigation_page(title_and_url_endpoint_pairs_list, title):
    """Generates a navigation menu with specified titles and corresponding
    links.
    
    Generates a simple navigation widjet which is created as a table
    containing button objects.
    
    Parameters
    ----------
    title_and_url_endpoint_pairs_list : list of string pairs
        Pairs of title and url strings.
        
    title : string
        Title of the table to create.
    
    Returns
    -------
    navigation_page : dash.html.Div
        dash.html.Div object containing the navigation widjet
    """
    
    navigation_page_contents = []
    
    navigation_page_contents.append( html.H1(title) )
    
    links_table_contents = []
    
    for title, full_url_endpoint in title_and_url_endpoint_pairs_list:
        
        
        table_row_element = html.Tr([html.Td(dcc.Link(html.Button(title, style={'width':'100%'}),
                                                      href=full_url_endpoint))])
        
        links_table_contents.append(table_row_element)
    
    
    navigation_page_contents.append(html.Table(links_table_contents, style={'margin-left': 'auto', 
                                                                            'margin-right': 'auto'}))
    
    navigation_page = html.Div(navigation_page_contents)
    
    return navigation_page
    

    
def generate_script_inference_widjet(script_sql_class):
    """Generates an inference widjet given the sql alchemy class representing
    experiment.
    
    Generates an inference widjet which allows to select trained models
    and see the qualitative results of the performance of the model
    on the uploaded by the user images
    
    Parameters
    ----------
    script_sql_class : sqlalchemy class
        Sql alchemy class to extract all the records from.
    
    Returns
    -------
    layout : dash.html.Div
        dash.html.Div object containing the widjet
    """

    script_type_name_id = script_sql_class.title.lower().replace(' ', '_')
    button_id = script_type_name_id + '-inference-refresh-button'
    data_table_id = script_type_name_id + '-inference-datatable'
    upload_widjet_id = script_type_name_id + '-inference-upload'
    output_div_id = script_type_name_id + '-inference-output-results'

    layout = html.Div([

            html.H1(script_sql_class.title),
            dt.DataTable(
                         rows=[{}],
                         id=data_table_id,
                         row_selectable=True,
                         filterable=True,
                         ),
            html.Button('Refresh Table', id=button_id),
            dcc.Upload(
            id=upload_widjet_id,
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
            },
           multiple=True
        ),
        html.Div(id=output_div_id)
    ])


    @app.callback(
    Output(data_table_id, 'rows'),
    [Input(button_id, 'n_clicks')])
    def callback(n_clicks):

        rows = generate_table_contents_from_sql_model_class(script_sql_class)

        return rows


    @app.callback(Output(output_div_id, 'children'),
                  [Input(upload_widjet_id, 'contents'),
                   Input(data_table_id, 'rows'),
                   Input(data_table_id, 'selected_row_indices')])
    def update_output(list_of_contents,
                      rows,
                      selected_row_indices):

        output = []

        if not list_of_contents:

            return output

        if not selected_row_indices:

            return output

        # TODO:
        # Generate page for each experiment type 
        # Make the display of the results more vivid (distinctive colors)
        # Correctly add additional inputs like filename and date of last update like here:
        # https://dash.plot.ly/dash-core-components/upload
        # When we tried last time it cause the function to be called multiple times instead of
        # just one

        selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)

        selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))

        extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()

        # expunge all the models instances (done)
        map(db.session.expunge, extracted_rows)
        
        
        for contents in list_of_contents:

            if contents is not None:
                
                content_type, content_string = contents.split(',')

                if 'image' in content_type:
                    
                    output.append(html.Img(src=contents))

                    for row in extracted_rows:

                        img_np = dash_deep.utils.convert_base64_image_string_to_numpy(content_string)

                        future_obj = task_manager.process_pool.schedule( script_sql_class.actions['inference'],
                                                                         args=(row, img_np) )

                        result_np = future_obj.result()

                        results_base64 = dash_deep.utils.convert_numpy_to_base64_image_string(result_np)


                        output.append( html.H1( "Result of model id#{}".format(row.id) ) )
                        output.append( html.Img(src=results_base64) )


        return output
    
    
    return layout


def generate_script_input_form_widjet(script_sql_class):
    """Generates an input form dash widjet given the sql alchemy class representing
    experiment.
    
    
    Parameters
    ----------
    script_sql_class : sqlalchemy class
        Sql alchemy class to extract all the records from.
    
    Returns
    -------
    form_widjet : dash.html.Div
        dash.html.Div object containing the input fields
    """
    
    form = generate_script_wtform_class_instance(script_sql_class)
    
    # TODO: when the form is displayed the click event is started
    # for some reason.
    
    # Since the wtform inherits the name of sqlalchemy script model
    # and they should have unique names
    id_prefix = form.__class__.__name__ + "-"
    
    # Here we will accumulate the input fields dash.html objects
    # that will be displayed to user
    elements_list = []
    
    # Here we will accumulate the dash.State objects that we will
    # use to read off the values provided by the user when the button
    # is pressed
    states_list = []
    
    for form_element in form:
        
        element_id_name = id_prefix + form_element.id
        
        html_label = html.Label(form_element.name)
        html_input_field = dcc.Input(id=element_id_name)
        states_list.append( State(element_id_name, 'value') )
        
        elements_list.append(html_label)
        elements_list.append(html_input_field)
    
    # Adding an element where we will output validation errors
    errors_element_id_name = id_prefix + 'Errors'
    errors_element = html.Div(id=errors_element_id_name,
                                  style={"color": "red"})
    elements_list.append(errors_element)
    
    # Adding a button
    button_element_id_name = id_prefix + 'run-script-button'
    button_element = html.Button('Run', id=button_element_id_name)
    elements_list.append(button_element)
    
    form_widjet = html.Div(elements_list)
    
    @app.callback(
    Output(errors_element_id_name, 'children'),
    [Input(button_element_id_name, 'n_clicks')],
    state=states_list)
    def press_event_callback(*arg):
        
        # The number of elements in the form can vary
        # first input argument is always number of clicks,
        # all other elements are inputs provided by user to the
        # form.
        user_input_form = arg[1:]
        
        for user_input, form_element in zip(user_input_form, form):
            
            form_element.data = user_input
        
        
        if form.validate():
            
            task_manager.schedule_task_from_form(form)
            
            return html.Div("The task was scheduled", style={'color': 'green'})
        else:
            
            return html.Div('Input validation error: {}'.format(
             form.errors
            ), style={'color': 'red'})
            
            
        
    return form_widjet


def generate_main_page_scripts_widjet(script_files_title_names, script_files_url_endpoints):
    """Generates a scripts main page dash widjet.
    
    Accepts script files titles and desired full url endpoints for each script file and
    creates a dash widject with titles which act as links for to repspective url endpoints.
    
    Parameters
    ----------
    script_files_title_names : list of strings
        List of strings representing the titles that will be used
        when displaying links.
    
    script_files_url_endpoints : list of strings
        List of strings representing the full url endpoints where
        the user will be redirected by pressing on the links
    
    Returns
    -------
    main_page_scripts_widjet_layout : dash.html.Div
        dash.html.Div object containing the main script page widjet
    """
    
    html_elements_list = []

    for script_file_title, script_file_url_endpoint in zip(script_files_title_names, script_files_url_endpoints):

        current_script_html_link = dcc.Link(script_file_title,
                                            href=script_file_url_endpoint)

        html_elements_list.append(current_script_html_link)
        html_elements_list.append(html.Br())
        
    main_page_scripts_widjet_layout = html.Div(html_elements_list)
        
    return main_page_scripts_widjet_layout



def generate_script_plots_widjet(script_sql_class):
    """Generates a script's result page widjet where we can inspect all results.
    
    Extracts all the records of a specified sqlalchemy class and puts them
    in a dash's data table + adds graph object where the loss and accuracy
    can be interactively inspected.
    
    Here we have a data table which can be refreshed by pressing the button --
    we reload all the records on button press event. Also, there is an interval
    object that updates the graph which contains the graphs of currently selected
    records in data table by user. Interval can be turned off by pressing radio button.
    This is needed in case we want to use the graph's advanced features like legends
    selection -- allows to leave out only selected curves ( this is not possible if we
    keep updating the graph with an interval).
    
    Parameters
    ----------
    script_sql_class : sqlalchemy class
        Sql alchemy class to extract all the records from.
    
    Returns
    -------
    layout : dash.html.Div
        dash.html.Div object containing the script results widjet
    """
    
    script_type_name_id = script_sql_class.title.lower().replace(' ', '_')
    interval_object_name_id = script_type_name_id + '-update-interval'
    button_id = script_type_name_id + '-button'
    graph_id_name = script_type_name_id + '-graph'
    data_table_id = script_type_name_id + '-datatable'
    radio_button_id = script_type_name_id + '-radio-button'
    
    #initial_table_contents = generate_table_contents_from_sql_model_class(script_sql_class)
    
    layout = html.Div([

            html.H1(script_sql_class.title),
            dcc.Interval(id=interval_object_name_id, interval=1000),
            dcc.Graph(
                      id=graph_id_name,
                      figure={'data':[], 'layout': []}
                     ),
            dcc.RadioItems(id=radio_button_id,
                           value=1000,
                           options=[
                                {'label': 'Graph live update on', 'value': 1000},
                                {'label': 'Graph live update off', 'value': 60*60*1000} # One hour -- max possible interval. Now way to just turn off the interval, so we apply this hack
                            ]),
            dt.DataTable(
                         rows=[{}],#initial_table_contents,
                         id=data_table_id,
                         row_selectable=True,
                         filterable=True,
                         ),
            html.Button('Refresh Table', id=button_id)
    ])
        
    @app.callback(
    Output(data_table_id, 'rows'),
    [Input(button_id, 'n_clicks')])
    def callback(n_clicks):
    
        rows = generate_table_contents_from_sql_model_class(script_sql_class)
        
        return rows
    
    @app.callback(
    Output(graph_id_name, 'figure'),
    [Input(data_table_id, 'rows'),
     Input(data_table_id, 'selected_row_indices'),
     Input(interval_object_name_id, 'n_intervals')])
    def callback(rows, selected_row_indices, n_intervals):
        
        print(rows)
        print(selected_row_indices)
        
        if not selected_row_indices:
            
            return {'data':[], 'layout':[]}
        
        selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)
        
        selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))
        
        extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()
        
        mutual_plot = create_mutual_plot(extracted_rows)
        
        return mutual_plot
    
    
    @app.callback(
    Output(interval_object_name_id, 'interval'),
    [Input(radio_button_id, 'value')])
    def update_interval(value):
        
        return value
    
    
    return layout



def generate_dataset_management_widjet(sql_model):
    """Generates a dataset management widjet given the sql alchemy class
    representing experiment.
    
    Generates a widjet where user can upload new samples for the selected
    dataset, annotate them or load a respective annotation file. Also, the
    already loaded samples' annotations can be updated using this widjet.
    
    Parameters
    ----------
    sql_model : sqlalchemy class
        Sql alchemy class to extract all the records from.
    
    Returns
    -------
    layout : dash.html.Div
        dash.html.Div object containing the widjet
    """
    
    trainset = sql_model.datasets['train']
    
    
    # Temporary function for overlay of segmentation masks
    # So far we only support binary mask, but in a future,
    # we will support multi-class masks
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

        encoded_image = dash_deep.utils.convert_numpy_to_base64_image_string(image)

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

        encoded_image = dash_deep.utils.convert_numpy_to_base64_image_string(img)

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


    script_type_name_id_prefix = sql_model.title.lower().replace(' ', '_') + '-'

    image_upload_id_name = script_type_name_id_prefix + 'image-upload'
    annotation_upoad_id_name = script_type_name_id_prefix + 'annotation-upload'
    sample_preview_graph_id_name = script_type_name_id_prefix + 'sample-preview-graph'
    add_new_sample_button_id_name = script_type_name_id_prefix + 'add-new-sample-button'
    dummy_output_id_name = script_type_name_id_prefix + 'dummy-output'
    global_crop_coordinates_id_name = script_type_name_id_prefix + 'global-crop-coordinates'
    crop_selection_previous_state_id_name = script_type_name_id_prefix + 'crop-selection-previous-state'
    annotation_selection_previous_state_id_name = script_type_name_id_prefix + 'annotation-selection-previous-state'
    annotation_dropdown_id_name = script_type_name_id_prefix + 'annotation-dropdown'
    annotation_class_select_radio_id_name = script_type_name_id_prefix + 'annotation-class-select-radio'
    annotation_refresh_button_id_name = script_type_name_id_prefix + 'annotation-refresh-button'
    delete_sample_button_id_name = script_type_name_id_prefix + 'delete-sample-button'
    annotation_graph_id_name = script_type_name_id_prefix + 'annotation-graph'
    add_new_sample_button_previous_state_id_name = script_type_name_id_prefix + 'add-new-sample-previous-n-clicks'


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

        image_np = dash_deep.utils.convert_base64_image_string_to_numpy(image_contents)
        output_image = image_np

        if is_annotation_loaded:

            annotation_np = dash_deep.utils.convert_base64_image_string_to_numpy(annotation_contents)
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

        image_np = dash_deep.utils.convert_base64_image_string_to_numpy(image_contents)
        annotation_np = np.zeros((image_np.shape[0], image_np.shape[1]),
                                 dtype=np.uint8)

        if is_annotation_loaded:

            annotation_np = dash_deep.utils.convert_base64_image_string_to_numpy(annotation_contents)

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
    
    return layout