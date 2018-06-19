import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

from dash_deep.app import app, task_manager
from dash_deep.sql import (get_column_names_and_values_from_sql_model_instance,
                           get_column_names_from_sql_model_class)

from dash_deep.app import db
import dash_table_experiments as dt
from dash_deep.plot import create_mutual_plot
from dash_deep.sql import generate_table_contents_from_sql_model_class


def generate_widjet_from_form(form):
    """Generates an input form dash widjet given the wtf form object.
    
    Wtf form can be easily created from sqlalchemy model object. Later on,
    the input fields can be also validated using wtf form.
    
    Parameters
    ----------
    form : instance of wtforms.Form
        Instance of wtform which can be created from sqlalchemy model
        automatically wtforms.ext.sqlalchemy.orm.model_form() function.
    
    Returns
    -------
    form_widjet : dash.html.Div
        dash.html.Div object containing the input fields
    """
    
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



def generate_script_results_widjet(script_sql_class):
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