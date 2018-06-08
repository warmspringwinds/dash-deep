import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from dash_deep.app import app, task_manager
from dash_deep.sql import (get_column_names_and_values_from_sql_model_instance,
                           get_column_names_from_sql_model_class)

import dash_table_experiments as dt
from dash_deep.app import db
from dash_deep.plot import create_mutual_plot


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
    
    script_type_name_id = script_sql_class.title.lower().replace(' ', '_')
    interval_object_name_id = script_type_name_id + '-update-interval'
    output_object_name_id = script_type_name_id + '-output-interval'
    button_id = script_type_name_id + '-button'
    graph_id_name = script_type_name_id + '-graph'
    
    
    layout = html.Div([

            html.H1(script_sql_class.title),
            dcc.Interval(id=interval_object_name_id, interval=1000),
            html.Div(id=output_object_name_id),
            dcc.Graph(
                      id='graph_id_name',
                      figure={'data':[], 'layout': []}
                     ),
            dt.DataTable(
                         rows=[{}],
                         id='datatable',
                         row_selectable=True,
                         filterable=True,
                         ),
            html.Button('Refresh Table', id=button_id)
    ])
    
    
    @app.callback(
    Output('datatable', 'rows'),
    [Input(button_id, 'n_clicks')])
    def callback(n_clicks):
    
        # Check on if we have created tables already
        # TODO: should be probably a better way
        experiments = []

        if db.engine.has_table(script_sql_class.__tablename__):

            experiments = script_sql_class.query.all()

        # TODO: update the sql query to fetch
        # all field except the graphs'
        rows = []

        for experiment in experiments:

            rows.append( get_column_names_and_values_from_sql_model_instance(experiment) )

        for row in rows:

            del row['graphs']
        
        return rows
    
    
    @app.callback(
    Output('graph_id_name', 'figure'),
    [Input('datatable', 'rows'),
     Input('datatable', 'selected_row_indices'),
     Input(interval_object_name_id, 'n_intervals')])
    def callback(rows, selected_row_indices, n_intervals):
        
        print(rows)
        print(selected_row_indices)
        
        selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)
        
        selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))
        
        extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()
        
        mutual_plot = create_mutual_plot(extracted_rows)
        
        return mutual_plot

    
    return layout