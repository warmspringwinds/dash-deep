import pebble

# Monkey-patching pebble to make its children non-daemonic
# We need this in order to allow children to spawn processes too
# Children should be able to spawn processes too because data loading
# routings in ml scripts usually spawn multiple processes in order to 
# load data faster.

# Read the doc of TaskManager.shutdown() for more information about this.

from multiprocessing import Process

def launch_process_patched(function, *args, **kwargs):
    
    process = Process(target=function, args=args, kwargs=kwargs)
    process.daemon = False
    process.start()

    return process


import pebble.pool.process

pebble.pool.process.launch_process = launch_process_patched

from dash_deep.app import db

class TaskManager():
    
    def __init__(self):
        
        # TODO: forward addtional arguments to ProcessPool()
        # function invocation in order to give users full control
        
        # Initializing process pool that will be used under the hood
        # to schedule all the tasks and get 'future' object as a return value
        
        # Important!!!: max_tasks=1 means that after performing each
        # task process is restarted. This is because there is no other
        # way to make deep learning frameworks to fully free up the gpu
        # memory that they have used other than stopping the process.
        # https://pebble.readthedocs.io/en/latest/#pebble.ProcessPool
        self.process_pool = pebble.ProcessPool(max_tasks=1)
        
        # This list is responsible for storing 'future' object of every
        # scheduled task
        self.tasks_list = []
        
    def schedule_task_from_form(self, form):
        """Spawns a process with task that was attached to a wtform and collected
        arguments from user.
    
        Uses a wtform that was filled out by user through web input form and
        validated. ```.actions``` is an additional paramerer added by our library
        that specifies a function to call once the form was validated.

        Parameters
        ----------
        form : instance of wtforms.Form
            Instance of wtform which can be created from sqlalchemy model
            automatically wtforms.ext.sqlalchemy.orm.model_form() function and
            with additional ```.actions``` parameter (see above).

        """
        
        # TODO: so far we are using only one name 'main' which
        # should be defined in the experiment model, but we had and idea
        # to use multiple names like 'initiate', 'run', 'conclude', 'on_error' which can
        # be run before, during, after, in case of error successful execution of a specified task
        
        # Creating a new sql model instance
        sql_model_instance = form.sql_model_class()
        
        # Populating the instance with the values from a filled-out form
        form.populate_obj(sql_model_instance)
        
        # Adding the new instance to the session and saving it to a database
        db.session.add(sql_model_instance)
        db.session.commit()
        
        # Since .commit() marks all fields of instances as 'expired'
        # we need to refresh all fields. It also has a nice side-effect
        # that values get coerced to a correct type from a string (Since
        # all values in our filled-out form are strings).
        db.session.refresh(sql_model_instance)
        
        # Detaching our object from a session, since we need to pass it
        # to another process and connect to the session of that session.
        # We also use this detached instance to display the id of the experiment
        # in the 'active tasks' table.
        db.session.expunge(sql_model_instance)
        
        # TODO: add additional field to the  stored future objects that will
        # store the detached instace of sql model.
        
        future_obj = self.process_pool.schedule(form.actions['main'],
                                                args=[sql_model_instance])
        
        self.tasks_list.append(future_obj)
   
    def shutdown(self):
        """Stops all the running jobs.
    
        Cancels all the running processes. We need this in order to stop all
        jobs in case the server receives a signal to shutdown. This way we avoid
        orphaned processes which might appear in case we don't run this when shutting down
        the server.
        
        We call this method whenever the main application throws and exception --
        this way in case the server has an internal problem or if it receives
        KeyboardInterrupt, we stop all spawned processes, therefore, avoiding
        orphaned processes. This is performed in the if __name__ == '__main__':
        section of dash_deep/index.py.
        
        See discussion here:
        https://github.com/noxdafox/pebble/issues/31

        """
        
        self.process_pool.stop()
        
        self.process_pool.join()
        