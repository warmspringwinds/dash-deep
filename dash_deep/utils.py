from wtforms import Form
from wtforms.ext.sqlalchemy.orm import model_form



def generate_script_wtform_classes(scripts_db_models):
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
    script_wtform_classes : list of wtforms.ext.sqlalchemy.orm classes
        List of classes representing wtforms for each sql models of a script.
    """
    
    def get_wtform_script_class(script_db_model):
        
        script_wtform_class = model_form(script_db_model, Form)
        
        return script_wtform_class
    
    script_wtform_classes = map(lambda script_db_model: get_wtform_script_class(script_db_model),
                                scripts_db_models)
    
    return script_wtform_classes


def get_script_files_basenames(script_db_models):
    """Generates basenames (without .py ext though) for each sqlalchemy model class representing a script.
    
    Extracts the script name of a file in dash_deep/scripts/ folder in which the sqlalchemy
    model class was defined. These names are later on used on the scripts/ front page.
    
    Parameters
    ----------
    script_db_models : list of sqlalchemy classes
        List containing sqlalchemy classes which represent each script.
    
    Returns
    -------
    script_display_names : list of strings
        List of strings where each string represents basename of a script file.
    """
    
    def get_parent_module_name(class_object):
        
        return class_object.__module__.split('.')[-1]

    script_files_basenames = map(lambda script_db_model:get_parent_module_name(script_db_model),
                               script_db_models)
    
    return script_files_basenames


def convert_script_files_basenames_to_title_names(script_files_basenames):
    """Converts script files basenames to title names that will be displayed to user.
    
    Takes name of each script, capitalizes it and replaces underscores with spaces.
    
    Parameters
    ----------
    script_files_basenames : list of script files basenames
        list of script files basenames that can be acquired with the help of get_script_files_basenames().
    
    Returns
    -------
    script_title_names : list of strings
        List of strings representing titles for each script.
    """
    
    
    def capitalize_and_remove_underscores(script_file_basename):
        
        return script_file_basename.title().replace('_', ' ')
    
    script_title_names = map(lambda script_file_basename: capitalize_and_remove_underscores(script_file_basename),
                             script_files_basenames)
    
    return script_title_names


def convert_script_files_basenames_to_url_endpoints(script_files_basenames,
                                                    parent_url_endpoint='/scripts/'):
    """Converts script files basenames to full url endpoints.
    
    Takes name of each script and appends the parent_url_endpoint to it. The forms
    for running scripts will be placed on these endpoints.
    
    Parameters
    ----------
    script_files_basenames : list of script files basenames
        list of script files basenames that can be acquired with the help of get_script_files_basenames().
    
    Returns
    -------
    script_files_url_endpoints : list of strings
        List of strings representing url endpoints.
    """
    
    def append_parent_url_endpoint_to_script_file_basename(script_file_basename):
        
        return parent_url_endpoint + script_file_basename
    
    script_files_url_endpoints = map(lambda script_file_basename: append_parent_url_endpoint_to_script_file_basename(script_file_basename),
                                     script_files_basenames)
    
    return script_files_url_endpoints


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
    script_title_names : list of strings
        List of strings representing titles for each script.
        
    script_files_url_endpoints : list of strings
        List of strings representing url endpoints.
    """
    
    script_files_basenames = get_script_files_basenames(script_db_models)

    script_files_url_endpoints = convert_script_files_basenames_to_url_endpoints(script_files_basenames)

    script_files_title_names = convert_script_files_basenames_to_title_names(script_files_basenames)
    
    return script_files_title_names, script_files_url_endpoints
    
    