from collections import OrderedDict


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