import dash_html_components as html
import dash_core_components as dcc


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
    
    elements_list = []
    
    for form_element in form:
        
        html_label = html.Label(form_element.name)
        html_input_field = dcc.Input(id=form_element.id)
        
        elements_list.append(html_label)
        elements_list.append(html_input_field)
    
    button_element = html.Button('Run', id='run-experiment-button')
    elements_list.append(button_element)
    
    form_widjet = html.Div(elements_list)
    
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

        current_script_html_link = dcc.Link(script_files_title_names,
                                            href=script_file_url_endpoint)

        html_elements_list.append(current_script_html_link)
        html_elements_list.append(html.Br())
        
    main_page_scripts_widjet_layout = html.Div(html_elements_list)
        
    return main_page_scripts_widjet_layout

