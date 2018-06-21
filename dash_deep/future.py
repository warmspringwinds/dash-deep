
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
    
    table = []
    
    for index, future_object in enumerate(future_objects):
        
        table_row = generate_table_row_from_future_object(future_object)
        table_row['id'] = index
        table.append(table_row)
        
    
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
    
    table_row_dict['error traceback'] = 'None'
    
    # If we call .exception() on a future object that was
    # cancelled, it will raise an exception, this is why
    # we also check for that. Cancelled processes usually
    # don't have exceptions
    if future_object.done() and (not future_object.cancelled()):
        
        exception = future_object.exception()
        
        if exception:
            
            table_row_dict['error traceback'] = str(exception.traceback)
    
    return table_row_dict