import click
from dash_deep.app import app


def generate_click_cli(wtform_instance, function):
    """Generates a command-line interface from a wtform and a function that 
    will be invoked with the input parameters of the form.
    
    Wtforms and click command line interface are used together to get user input,
    validate it and populate sqalchemy instance later on.
    
    Parameters
    ----------
    wtform_instance : instance of wtform class
        Wtform instace that was generated from sqlalchemy model
        
    function : function object
        A function that will be called with collected arguments.
        It's better to use kawargs when writing this kind of a function.
    
    Returns
    -------
    command : click.core.Command
        Instance of command class of click. To invoke input interface use:
        if __name__ == '__main__':
            command()
         
    """
    
    # TODO: since we have a form object we can create one more 
    # decorator to automatically validate the input to the function
    # this way we can have the validation also in the command line
    # interface and not only in the web UI.
    
    command = function
    
    for input_field in wtform_instance:
        
        command = click.argument(input_field.name)(command)

    command = click.command()(command)
    
    return command