from dash_deep.app import db

from time import sleep
import click

import torch

# TODO: click for some reason ignores newline characters so we had to use
# more break symbols than necessary

def run(batch_size, learning_rate):
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
    
    
    epochs = range(30)
    
    # Creates a progress bar.
    #with click.progressbar(epochs) as epochs:
        
    for epoch in epochs:

        sleep(1)
    
    
    return 'success'