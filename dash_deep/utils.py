import os
from dash_deep.cli.cli_factory import generate_script_input_form_cli_interface

from dash_deep.widjets.widjets_factory import (generate_script_input_form_widjet,
                                               generate_script_plots_widjet,
                                               generate_script_inference_widjet)

import re
import base64
import numpy as np
from PIL import Image
from io import BytesIO


def convert_numpy_to_base64_image_string(image_np):
    """Converts a numpy image representation to a base64 encoding
    of the image file with a metadata that is necessary to display it in 
    
    Dash's image object can display images encoded in base64 format if
    they have necessary metadata flags which we also add.
    
    Parameters
    ----------
    image_np : numpy ndarray (dtype=np.uint8)
        numpy ndarray (dtype=np.uint8)
    
    Returns
    -------
    base64_img_string_with_metadata : string
        string
    """
    
    image_pil = Image.fromarray(image_np)
    
    buffer = BytesIO()
    image_pil.save(buffer, format="JPEG")
    base64_img_string = base64.b64encode(buffer.getvalue())
    
    base64_img_string_with_metadata = "data:image/jpg;base64,{}".format(base64_img_string)
    
    return base64_img_string_with_metadata


def convert_base64_image_string_to_numpy(base64_image_string):
    """Converts an image string in the base64 encoding into a numpy
    array.
    
    Dash's Upload element returns uploaded images as a base64 encoded string
    with prepended metadata info. In this function we remove this metadata and
    convert the leftover string into numpy image.
    
    Parameters
    ----------
    base64_image_string : string
        Base64 encoded image string.
    
    Returns
    -------
    img_np : numpy ndarray
        Ndarray representation of an image.
        
    """
    
    
    # Removing the metadata flag, read more here:
    # https://stackoverflow.com/a/26085215
    base64_image_string_without_metadata = re.sub('^data:image/.+;base64,', '', base64_image_string)
            
    # Deconding the 
    img_np = np.asarray( Image.open(BytesIO(base64.b64decode(base64_image_string_without_metadata))) )
    
    return img_np
    
    

def generate_model_save_file_path(experiment_sql_model_instance):
    """Generates a save path of experiment model relative to the folder
    where all the models are being saved (usually relative to ~/.dash-deep/models.
    
    The function assumes that the field `created_at` is present in the model
    and is initialized. The model save path is composed following the rule:
    experiment_title/year/month/day/experiment_title-daytime.pth. By prepending
    `~/.dash-deep/models/` to the returned string, you will get the full path
    to the saved model file.
    
    Parameters
    ----------
    experiment_sql_model_instance : instance of sqlalchemy model class
        Sql alchemy model class instance
    
    Returns
    -------
    full_path : string
        String representing the model save path.
        
    """
    
    date = experiment_sql_model_instance.created_at.date()
    time = experiment_sql_model_instance.created_at.time()
    
    # Converting title to a name with spaces replaced with dashes
    experiment_type_folder_name = experiment_sql_model_instance.title.lower().replace(' ', '-')

    date_folder_path = os.path.join(str(date.year),
                                    str(date.month),
                                    str(date.day))
    
    # Replace everything in the time with dashes
    day_time_string = str(time).replace(':', '-').replace('.', '-')

    filename = experiment_type_folder_name + '-' + day_time_string + '.pth'
    
    full_path = os.path.join(experiment_type_folder_name,
                             date_folder_path,
                             filename)
    
    return full_path


def get_script_titles_url_endpoints_and_cli_names(script_db_models):
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
    
    script_cli_names : list of strings
        List of strings representing comman line names of commands.
        
    """
    
    script_titles = []
    script_cli_names = []
    script_full_url_endpoints = []
    
    for script_db_model in script_db_models:
        
        script_title = script_db_model.title
        script_titles.append(script_title)
        
        script_url_endpoint = script_title.lower().replace(' ', '_')
        script_cli_names.append(script_url_endpoint)
        
        current_script_endpoints = {}
        
        new_script_input_form_widjet = generate_script_input_form_widjet(script_db_model)
        current_script_endpoints['train'] = ("/{}/train".format( script_url_endpoint ), new_script_input_form_widjet)
        
        inference_widjet = generate_script_inference_widjet(script_db_model)
        current_script_endpoints['inference'] = ("/{}/inference".format( script_url_endpoint ), inference_widjet)
        
        plots_widjet = generate_script_plots_widjet(script_db_model)
        current_script_endpoints['plot'] = ("/{}/plot".format( script_url_endpoint ), plots_widjet)
        
        script_full_url_endpoints.append(current_script_endpoints)
        
    
    return script_titles, script_full_url_endpoints, script_cli_names
    