from wtforms import Form
from wtforms.ext.sqlalchemy.orm import model_form
from dash_deep.widjets.widjets_factory import generate_widjet_from_form


def generate_wtform_instances_and_input_form_widjets(scripts_db_models):
    """Generates wtform classes instances and input form widjets for each sqlalchemy model
    representing a script.
    
    Wtforms and input widjets are used together to get user input, validate it
    and populate sqalchemy instance later on.
    
    Parameters
    ----------
    script_db_models : list of sqlalchemy classes
        List containing sqlalchemy classes which represent each script.
    
    Returns
    -------
    script_wtform_classes_instances : list of wtforms.ext.sqlalchemy.orm classes instances
        List of classes instances representing wtforms for each sql models of a script.
        
    scripts_input_form_widjets : list of dash.html.Div instances
        List containing the dash input forms for each script. 
    """
        
    wtform_classes_instances = generate_script_wtform_instances(scripts_db_models)

    scripts_input_form_widjets = generate_scripts_input_form_widjets(wtform_classes_instances)
    
    return wtform_classes_instances, scripts_input_form_widjets


def generate_scripts_input_form_widjets(scripts_wtform_classes_instances):
    """Generates input form dash widjets for each wtform class representing a script.
    
    By doing this we avoid code duplicating as all the name of the fields and requirements
    are defined in the sqlalchemy model class already.
    
    Parameters
    ----------
    scripts_wtform_classes_instances : list of wtforms.ext.sqlalchemy.orm classes instances
        List containing classes instances representing script input form.
    
    Returns
    -------
    scripts_input_form_widjets : list of dash.html.Div instances
        List containing the dash input forms for each script. 
    """
    
    scripts_input_form_widjets = []
    
    for wtform_class_instance in scripts_wtform_classes_instances:
        
        script_input_form_widjet = generate_widjet_from_form(wtform_class_instance)
        
        scripts_input_form_widjets.append(script_input_form_widjet)
    
    return scripts_input_form_widjets


def generate_script_wtform_instances(scripts_db_models):
    """Generates wtforms.ext.sqlalchemy.orm classes for each script database class. 
    
    As most requirements to the input fields are specified in the classes of sql
    models representing each script -- we can automatically create wtform classes
    for each of them. This wtforms are later on used to generate input form widjets
    for each script and to validate the user inputs + populate the sql model objects.
    
    Parameters
    ----------
    script_db_models : list of sqlalchemy classes
        List containing sqlalchemy classes which represent each script.
    
    Returns
    -------
    script_wtform_class_instances : list of wtforms.ext.sqlalchemy.orm classes instances
        List instances of classes representing wtforms for each sql models of a script.
    """
    
    def get_wtform_script_class_instance(script_db_model):
        
        script_wtform_class = model_form(script_db_model, Form)
        
        script_wtform_class_instance = script_wtform_class()
        
        # Copying the the actions field defined by the user in the model
        # into the wtform instance. This action will be triggered
        # once the form is validated
        script_wtform_class_instance.actions = script_db_model.actions
        
        return script_wtform_class_instance
    
    script_wtform_class_instances = map(lambda script_db_model: get_wtform_script_class_instance(script_db_model),
                                        scripts_db_models)
    
    return script_wtform_class_instances



def get_script_titles_and_url_endpoints(script_db_models):
    """Generates titles and url endpoints for each script from its sqlalchemy model class.
    
    Converts sqlalchemy class for each script into title and url endpoint that will be used
    on the front page of all scripts.
    
    Parameters
    ----------
    script_db_models : list of sqlalchemy classes
        List containing sqlalchemy classes which represent each script.
    
    Returns
    -------
    script_titles : list of strings
        List of strings representing titles for each script.
        
    script_full_url_endpoints : list of strings
        List of strings representing url endpoints.
    """
    # Extracting the .title attribute
    script_titles = map(lambda script_db_model: script_db_model.title, script_db_models)
    
    # Lowercasing title and replacing spaces with underscores
    script_url_endpoints = map(lambda script_title: script_title.lower().replace(' ', '_'),
                          script_titles)
    
    # Appending the global url endpoint responsible for all scripts forms
    script_full_url_endpoints = map(lambda script_url_endpoint: '/scripts/' + script_url_endpoint,
                                    script_url_endpoints) 
    
    return script_titles, script_full_url_endpoints
    