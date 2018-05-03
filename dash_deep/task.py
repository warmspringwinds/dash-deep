from pebble import ProcessPool


class TaskManager():
    
    def __init__(self):
        
        # TODO: forward addtional arguments to ProcessPool()
        # function invocation in order to give users full control
        
        # Initializing process pool that will be used under the hood
        # to schedule all the tasks and get 'future' object as a return value
        self.process_pool = ProcessPool()
        
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
        