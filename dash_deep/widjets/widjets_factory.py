import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from dash_deep.app import app, task_manager


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
        
    layout = html.Div([

            html.H1(script_sql_class.title),
            dcc.Interval(id=interval_object_name_id, interval=1000),
            html.Div(id=output_object_name_id),
            dcc.Graph(
                    id='graph-1',
                    figure={'data':[], 'layout': []})
                ])

    @app.callback(
        Output('graph-1', 'figure'),#Output(output_object_name_id, 'children'),
        [Input(interval_object_name_id, 'n_intervals')])
    def display_output(n):
        
        experiments = script_sql_class.query.all()
        first_experiment = experiments[0]
        first_experiment_graph = first_experiment.graphs

        return first_experiment_graph.figure_obj
    
    
    return layout
    
