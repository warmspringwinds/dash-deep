from dash_deep.cli.cli_factory import generate_script_input_form_cli_interface

from dash_deep.widjets.widjets_factory import (generate_script_input_form_widjet,
                                               generate_script_plots_widjet,
                                               generate_script_inference_widjet,
                                               generate_script_navigation_page,
                                               generate_dataset_management_widjet)
import os
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


def generate_scripts_widjets_and_cli_interfaces(script_db_models):
    """ Generates lookup table with url to widjet mapping and cli interfaces
    for each script.
    
    Returns the index page widjet which contains links to other script
    control pages where user can start, track plots and perform inference
    using trained models. Also returns the cli interface which can be used
    to start new experiment through command line interface.
    
    Parameters
    ----------
    script_db_models : list of sqlalchemy classes
        List containing sqlalchemy classes which represent each script.
    
    Returns
    -------
    
    index_page : dash widjet
        Dash widjet containing main page navigation menu
        
    scripts_full_url_widjet_look_up_table : dict
        Dict that maps full urls into Dash widjet
    
    scripts_name_and_cli_instance_pairs : list of tuples
        List with string cli_interface pairs where string
        represents the cli interface name
        
    """
    
    scripts_full_url_widjet_look_up_table = {}
    scripts_name_and_cli_instance_pairs = []
    
    index_page_nav_bar_content = [('GPU utilization', '/gpu'),
                                  ('Tasks tracking', '/tasks')]
    
    for script_db_model in script_db_models:
        
        script_title = script_db_model.title
        script_name = script_title.lower().replace(' ', '_')
        script_cli_instance = generate_script_input_form_cli_interface(script_db_model)
        scripts_name_and_cli_instance_pairs.append( (script_name, script_cli_instance) )
        
        script_main_page_url = "/{}".format(script_name)
        script_train_page_url = "/{}/train".format( script_name )
        script_plot_page_url = "/{}/plot".format( script_name )
        script_inference_page_url = "/{}/inference".format( script_name )
        script_dataset_management_url = "/{}/dataset_management".format( script_name )
        
        index_page_nav_bar_content.append((script_title, script_main_page_url))
        
        script_main_page_nav_bar_content = [('GPU utilization', '/gpu'),
                                            ('Tasks tracking', '/tasks'),
                                            ('Train', script_train_page_url),
                                            ('Plot', script_plot_page_url),
                                            ('Inference', script_inference_page_url),
                                            ('Dataset Management', script_dataset_management_url)]
        
        script_main_page_widjet = generate_script_navigation_page(script_main_page_nav_bar_content,
                                                                  script_title)
 
        scripts_full_url_widjet_look_up_table[script_main_page_url] = script_main_page_widjet
       
        new_script_input_form_widjet = generate_script_input_form_widjet(script_db_model)
        scripts_full_url_widjet_look_up_table[script_train_page_url] = new_script_input_form_widjet 
        
        inference_widjet = generate_script_inference_widjet(script_db_model)
        scripts_full_url_widjet_look_up_table[script_inference_page_url] = inference_widjet
        
        plots_widjet = generate_script_plots_widjet(script_db_model)
        scripts_full_url_widjet_look_up_table[script_plot_page_url] = plots_widjet
        
        dataset_management_widjet = generate_dataset_management_widjet(script_db_model)
        scripts_full_url_widjet_look_up_table[script_dataset_management_url] = dataset_management_widjet
    
    index_page = generate_script_navigation_page(index_page_nav_bar_content, 'Main')
        
    
    return index_page, scripts_full_url_widjet_look_up_table, scripts_name_and_cli_instance_pairs
    