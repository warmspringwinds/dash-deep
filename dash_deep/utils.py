

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