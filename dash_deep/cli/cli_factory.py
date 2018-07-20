import click
from dash_deep.sql import generate_script_wtform_class_instance


def generate_script_input_form_cli_interface(script_db_model):
    """Generates a command-line interface from for sql_alchemy class
    representing a script.
    
    Parameters
    ----------
    script_db_model : sqlalchemy classes
        sqlalchemy class representing script.
        
    Returns
    -------
    command : click.core.Command
        Instance of command class of click. To invoke input interface use:
        if __name__ == '__main__':
            command()
         
    """
    
    wtform_instance = generate_script_wtform_class_instance(script_db_model)
    
    # TODO: since we have a form object we can create one more 
    # decorator to automatically validate the input to the function
    # this way we can have the validation also in the command line
    # interface and not only in the web UI.
    
    command = wtform_instance.actions['main']
    
    for input_field in wtform_instance:
        
        command = click.argument(input_field.name)(command)

    command = click.command()(command)
    
    return command