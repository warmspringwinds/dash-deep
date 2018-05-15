from dash_deep.app import db
from time import sleep
import torch


def run(batch_size,
        learning_rate):
    
    # Probably should also provide initiated db class object
    print('started the classification job')
    
    test = torch.ones(100, 100, 10).cuda()
    
    # Simulate training
    sleep(5)
    
    print('finished the job')
    
    # populated_object.batch_size = '555'
    # populated_object.learning_rate = '100'
    # populated_object.output_stride = '777'

    # db.session.add(populated_object)
    # db.session.commit()
    
    return 'success'