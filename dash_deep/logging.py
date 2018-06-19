from dash_deep.app import db
from sqlalchemy.orm.attributes import flag_modified


class Experiment():
    
    def __init__(self, sql_model_instance):
        
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
        
        
    def add_next_iteration_results(self, *args, **kwargs):
        
        # Passing all the parameters to the graph object
        # which upates the internal state of the graph
        self.sql_model_instance.graphs.add_next_iteration_results(*args, **kwargs)
        
        # Since we pickle this field -- we need to explicitly tell that
        # the field was updated, otherwise the changes won't be commited
        flag_modified(self.sql_model_instance, 'graphs')
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
    
    
    def update_best_iteration_results(self, **kwargs):
        
        column_names = self.sql_model_instance.graphs.graph_column_names
        
        for key, value in kwargs.iteritems():
            
            if key in column_names:
                
                setattr(self.sql_model_instance, key, value)
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
    
    def finish(self):
        
        # Compute the best results for each metric using graph object:
        # like highest accuracy + lowest loss -- and write them down
        # into database
        
        # Should we close the db session?
        
        self.db.session.add(self.sql_model_instance)
        self.db.session.commit()
        
        