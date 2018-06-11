
def generate_table_from_future_objects(future_objects):
    """Generates a table representation of provided concurrent.futures.Future
    objects.
    
    Generates a Dash's widjet table contents of running tasks. See
    generate_table_row_from_future_object() for more details.
    
    Parameters
    ----------
    future_object : list
        List of concurrent.futures.Future
    
    Returns
    -------
    table : list
        List of dicts that represent table rows.
    """
    
    table = map(lambda future_object: generate_table_row_from_future_object(future_object), future_objects)
    
    return table


def generate_table_row_from_future_object(future_object):
    """Generates a table row representation of a concurrent.futures.Future
    object.
    
    Generates a dict with attributes necessary for the tasks dash widjet table
    where all the running tasks are being displayed. We are retrieving the 'state'
    attribute of the provided future object which can be either cancelled, finished,
    failed or pending -- this state is being displayed later on to the user.
    
    Parameters
    ----------
    future_object : concurrent.futures.Future
        Future object
    
    Returns
    -------
    table_row_dict : dict
        Dict that describes provided future object
    """
    
    table_row_dict = {}
    
    # TODO: since we use a non public attribute it might
    # be changed in a future -- need to investigate more
    table_row_dict['state'] = future_object._state
    
    table_row_dict['errors'] = 'None'
    
    if future_object.done():
        
        exception = future_object.exception()
        
        if exception:
            
            table_row_dict['errors'] = exception
    
    return table_row_dict