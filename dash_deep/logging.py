from dash_deep.app import db
from sqlalchemy.orm.attributes import flag_modified


class Experiment():
    """Helper class that accepts the filled-out sql alchemy model
    instance and takes care of database connection in a newly created
    process. It also provides methods to easily append new values to the
    graph and update the current best results.
    
    """
    
    def __init__(self, sql_model_instance):
        """Initializes the new experiment instance from a populated
        sql alchemy model instance which is being provided to a function
        specified by user in the models.py module. The sql alchemy model
        instance is populated by user though the our provided gui.
    
        Parameters
        ----------
        sql_model_instance : sql alchemy model instance
            Sql alchemy model instace from models.py module.
        """
        
        #self.sql_model_instance = sql_model_instance
        
        # Since experiment will be most probably run in a separate,
        # process, we need to take appropriate actions to prevent different
        # processes from using the same connection:
        # http://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
        db.engine.dispose()
        self.db = db
        
        # Attaching the detached instance of sql model class to our session
        # Each process usually has its own session and we attach this object to it.
        self.sql_model_instance = self.db.session.merge(sql_model_instance)
    
    
    def start(self):
        """Starts the experiment.
        
        The function starts the experiment by commiting the experiment
        model instance to the database.
        """
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
        
        
    def add_next_iteration_results(self, *args, **kwargs):
        """Adds new values to populate the graph of the experiment with.
        The named arguments are equivalent to the trace names specified
        in the sql alchemy model definition in the models.py module.
    
        Parameters
        ----------
        kwargs : Named arguments
            Named arguments representing new values to append
            to the traces of the graph of the experiment.
        """
        
        # Passing all the parameters to the graph object
        # which upates the internal state of the graph
        self.sql_model_instance.graphs.add_next_iteration_results(*args, **kwargs)
        
        # Since we pickle this field -- we need to explicitly tell that
        # the field was updated, otherwise the changes won't be commited
        flag_modified(self.sql_model_instance, 'graphs')
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
    
    
    def update_best_iteration_results(self, **kwargs):
        """Updates values of the best results of trace
        values so far. Named arguments are equivalent to
        the ones in the add_next_iteration_results() method.
    
        Parameters
        ----------
        kwargs : Named arguments
            Named arguments representing the column
            names defined in the models.py
        """
        
        column_names = self.sql_model_instance.graphs.graph_column_names
        
        for key, value in kwargs.iteritems():
            
            if key in column_names:
                
                setattr(self.sql_model_instance, key, value)
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
    
    def finish(self):
        
        # TODO: add additional field to the models -- finished
        # and equate it to True on the completion of the exepriment.
        
        # Should we close the db session?
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
        
        