from dash_deep.app import db
from dash_deep.plot import BaseGraph
from datetime import datetime

# More examples on flask-sqlalchemy mixins:
# https://stackoverflow.com/questions/43386558/how-can-one-implement-mixin-in-flask

# In case of multiple inheritance for mixins and the execution of constructor
# functions of all the ancestor classes:
# https://stackoverflow.com/questions/3277367/how-does-pythons-super-work-with-multiple-inheritance

class BasicExperimentMixin(object):
    
    id = db.Column(db.Integer, primary_key=True)
    gpu_id = db.Column(db.Integer, nullable=False)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    model_path = db.Column(db.String(120), nullable=False)
    
    training_loss = db.Column(db.Float, nullable=False)
    training_accuracy = db.Column(db.Float, nullable=False)
    validation_accuracy = db.Column(db.Float, nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    graph_definition = [ 
                           [ ('Losses', ['training_loss']) ],
                           [ ('Accuracy', ['training_accuracy', 'validation_accuracy']) ]
                       ]
    
    exclude_from_form = ['graphs',
                         'training_loss',
                         'training_accuracy', 'validation_accuracy',
                         'created_at', 'model_path']
    
    def __init__(self, *args, **kwargs):
        
        super(BasicExperimentMixin, self).__init__(*args, **kwargs)
        
        self.gpu_id = 0
        self.batch_size = 100
        self.learning_rate = 0.0001
        
        self.created_at = datetime.utcnow()
        self.model_path = ''
        
        self.training_loss = 0.0
        self.training_accuracy = 0.0
        self.validation_accuracy = 0.0
        
        self.graphs = BaseGraph(self.graph_definition)