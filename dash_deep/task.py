import pebble

# Monkey-patching pebble to make its children non-daemonic
# We need this in order to allow children to spawn processes too
# Children should be able to spawn processes too because data loading
# routings in ml scripts usually spawn multiple processes in order to 
# load data faster.

# Problems that might occur:
# When there is a job that has already been started and the server
# recieves the sigterm, it will not kill the spawned jobs.

# TODO: Solution: listen to sigterm and manually go through array of
# pebble 'future' objects to stop them before quiting.

# See discussion here:
# https://github.com/noxdafox/pebble/issues/31
from multiprocessing import Process

def launch_process_patched(function, *args, **kwargs):
    
    process = Process(target=function, args=args, kwargs=kwargs)
    process.daemon = False
    process.start()

    return process


import pebble.pool.process

pebble.pool.process.launch_process = launch_process_patched



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
        future_obj = self.process_pool.schedule(form.actions['main'],
                                                kwargs=form.data)
        
        self.tasks_list.append(future_obj)
        