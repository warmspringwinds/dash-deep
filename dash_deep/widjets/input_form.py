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