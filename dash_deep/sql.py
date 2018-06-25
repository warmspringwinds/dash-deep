import random
from collections import OrderedDict
from sqlalchemy.orm.attributes import flag_modified

import dash_deep.models
from dash_deep.app import db


def generate_table_contents_from_sql_model_class(sql_model_class):
    """Extracts all records that are currently stored in the database
    of the specified class and prepares them to be passed to Dash's datatable.

    Fetches all the records from the database, removes the graph field and
    converts these records into list of dicts which is accepted by Dash's
    data table object. Has a special return value in case we don't have
    any records of the specified class in our database -- this is specific
    to Dash's data table.
    
    Parameters
    ----------
    sql_model_class : sqlalchemy model class
        sqlalchemy model class
    
    Returns
    -------
    rows : list
        List of dicts representing database records.
    """
    
    # Dash's data table needs to receive
    # this exact value in case when we want an empty table
    # TODO: maybe it can be done in a better way
    empty_return_value = [{}]
    
    if not db.engine.has_table(sql_model_class.__tablename__):
        
        return empty_return_value

    experiments = sql_model_class.query.all()
    
    if not experiments:
        
        return empty_return_value

    # TODO: update the sql query to fetch
    # all field except the graphs'
    rows = []

    for experiment in experiments:

        rows.append( get_column_names_and_values_from_sql_model_instance(experiment) )

    # Removing the graph field from our model since
    # we want to only put numerical values in our table
    for row in rows:

        del row['graphs']

    return rows

def get_column_names_and_values_from_sql_model_instance(sql_model_instance):
    """Extracts column names and associated values from and sqlalchemy model
    instance.

    Extracts names and values of each column as an ordered dict which has
    the same order as values acquired from get_column_names_from_sql_model_class()
    function.
    
    Parameters
    ----------
    sql_model_instance : sqlalchemy model instance
        sqlalchemy model instance
    
    Returns
    -------
    ordered_dict : collections.OrderedDict
        ordered dict of column names and values
    """
    
    return OrderedDict((column.name, getattr(sql_model_instance, column.name)) 
                for column in sql_model_instance.__table__.columns)


def get_column_names_from_sql_model_class(sql_model_class):
    """Extracts column names from and sqlalchemy model
    class

    Extracts names a list which has the same order as values acquired from
    get_column_names_and_values_from_sql_model_instance() function.
    
    Parameters
    ----------
    sql_model_class : sqlalchemy model class
        sqlalchemy model class
    
    Returns
    -------
    sql_model_field_names : list
        List with column names.
    """
    
    sql_model_field_names = []
    
    for col in sql_model_class.__table__.columns:
        
        sql_model_field_names.append(col.name)
    
    return sql_model_field_names


def create_dummy_endovis_record():
    """Creates sqlalchemy endovis model instance filled with random values. 

    The sqlalchemy model is created and filled out with random values -- 
    we choose from a certain set of predefined values which were hardcoded
    in the function. The function is used to fill out the database with dummy
    records for testing.
    
    Returns
    -------
    dummy_model_instance : list of sqlalchemy model instances
        list of sqlalchemy model instances
    """
    
    batch_size_choices = [100, 50, 10, 5, 1]
    learning_rate_choices = [1.0, 0.1, 0.01, 0.001]
    output_stride_choices = [8, 16, 32]
    
    def generate_radnom_decreasing_or_increasing_list(length, factor):
    
        output_list = []
        current_factor = factor

        for i in xrange(length):

            next_value = random.random() * current_factor
            current_factor = current_factor * factor

            output_list.append(next_value)


        return output_list
    
    dummy_model_instance = dash_deep.models.EndovisBinary()
    
    dummy_model_instance.batch_size = random.choice(batch_size_choices)
    dummy_model_instance.learning_rate = random.choice(learning_rate_choices)
    dummy_model_instance.output_stride = random.choice(output_stride_choices)

    dummy_model_instance.graphs.training_accuracy_history['x'] = range(100)
    dummy_model_instance.graphs.training_accuracy_history['y'] = generate_radnom_decreasing_or_increasing_list(100, 1.05)

    dummy_model_instance.graphs.validation_accuracy_history['x'] = range(100)
    dummy_model_instance.graphs.validation_accuracy_history['y'] = generate_radnom_decreasing_or_increasing_list(100, 1.05)

    dummy_model_instance.graphs.validation_loss_history['x'] = range(100)
    dummy_model_instance.graphs.validation_loss_history['y'] = generate_radnom_decreasing_or_increasing_list(100, 0.9)

    dummy_model_instance.graphs.training_loss_history['x'] = range(100)
    dummy_model_instance.graphs.training_loss_history['y'] = generate_radnom_decreasing_or_increasing_list(100, 0.9)
    
    # Not really necessary, but if you load a model and
    # update graph field, you need to call this function 
    # before commiting to a database
    flag_modified(dummy_model_instance, "graphs")
    
    return dummy_model_instance


def create_dummy_endovis_records(number_of_dummy_records):
    """Creates sqlalchemy endovis model instances filled with random values. 

    The sqlalchemy models are created and filled out with random values -- 
    we choose from a certain set of predefined values which were hardcoded
    in the function. The function is used to fill out the database with dummy
    records for testing.
    
    Parameters
    ----------
    number_of_dummy_records : int
        Number of dummy records to create.
    
    Returns
    -------
    dummy_model_instance : list of sqlalchemy model instances
        list of sqlalchemy model instances.
    """
    
    dummy_endovis_records_list = []
    
    for i in xrange(number_of_dummy_records):
        
        dummy_endovis_record = create_dummy_endovis_record()
        dummy_endovis_records_list.append(dummy_endovis_record)
        
    
    return dummy_endovis_records_list