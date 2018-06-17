from dash_deep.logging import Experiment

from time import sleep
import click

import torch
from random import random

# TODO: click for some reason ignores newline characters so we had to use
# more break symbols than necessary

def run(sql_db_model):
    """ Runs an imagenet training experiment.
    
    A dummy experiment that demonstrates an application
    for the problem of image classification on imagenet dataset.
    
    Parameters
    
    ----------
    
    batch_size : int
    
        Size of a batch to use during training.
    
    
    learning_rate : float
    
    
        Lerning rate to be used by optimization algorithm.
    """
    
    print( type(sql_db_model.batch_size) )
    
    experiment = Experiment(sql_db_model)
    
    print(type(experiment.sql_model_instance.batch_size))
    
    epochs = range(50)
            
    for epoch in epochs:
        
        
        experiment.add_next_iteration_results(random(),
                                              random(),
                                              random(),
                                              random())
        sleep(5)
    
    experiment.finish()
    
    return 'success'