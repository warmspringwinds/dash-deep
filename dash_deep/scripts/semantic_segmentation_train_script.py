from dash_deep.app import db
from time import sleep



def run(batch_size, learning_rate, output_stride):
    
    #db.engine.dispose()
    print('started the job')
    
    import torch
    
    test = torch.ones(100, 100, 10).cuda()
    
    # Simulate training
    sleep(5)
    
    print('finished the job')
    
    #del test
    
    #torch.cuda.empty_cache()
    
#     populated_object.batch_size = '555'
#     populated_object.learning_rate = '100'
#     populated_object.output_stride = '777'
    
#     db.session.add(populated_object)
#     db.session.commit()
    
    return 'success'

#PascalSegmentation.actions['main'] = run