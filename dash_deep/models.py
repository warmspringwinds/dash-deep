from dash_deep.app import db
from dash_deep.plot import BaseGraph
from datetime import datetime


from dash_deep.scripts.endovis_binary_segmentation_train import run as endovis_binary_segmentation_train_run


class EndovisBinary(db.Model):
    
    title = 'Endovis Binary Segmentation'
    id = db.Column(db.Integer, primary_key=True)
    
    gpu_id = db.Column(db.Integer, nullable=False)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    output_stride = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False)
    
    model_path = db.Column(db.String(120), nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    training_loss = db.Column(db.Float, nullable=False)
    
    training_accuracy = db.Column(db.Float, nullable=False)
    validation_accuracy = db.Column(db.Float, nullable=False)
    
    graph_definition = [ 
                           [ ('Losses', ['training_loss']) ],
                           [ ('Accuracy', ['training_accuracy', 'validation_accuracy']) ]
                       ]
    
    actions = {'main': endovis_binary_segmentation_train_run}
    
    exclude_from_form = ['graphs',
                         'training_loss',
                         'training_accuracy', 'validation_accuracy',
                         'created_at', 'model_path']
    
    def __init__(self, *args, **kwargs):
        
        super(EndovisBinary, self).__init__(*args, **kwargs)
        
        self.gpu_id = 0
        self.batch_size = 100
        self.learning_rate = 0.0001
        self.output_stride = 8
        
        self.created_at = datetime.utcnow()
        self.model_path = ''
        
        self.training_loss = 0.0
        self.training_accuracy = 0.0
        self.validation_accuracy = 0.0
        
        self.graphs = BaseGraph(self.graph_definition)
    
    def __repr__(self):
        
        return ('<Endovis Binary Segmentation experiment id={}, batch_size={}, learning_rate={}>, output_stride={}, graphs={}'.format(
                self.id,
                self.batch_size,
                self.learning_rate,
                self.output_stride,
                self.graphs))


from dash_deep.scripts.imagenet_classification_train import run as imagenet_classification_train_run
    
class ImagenetClassification(db.Model):
    
    title = 'Imagenet Classification'
    id = db.Column(db.Integer, primary_key=True)
    
    gpu_id = db.Column(db.Integer, nullable=False)
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False)
    
    model_path = db.Column(db.String(120), nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    training_loss = db.Column(db.Float, nullable=False)
    training_accuracy = db.Column(db.Float, nullable=False)
    validation_loss = db.Column(db.Float, nullable=False)
    validation_accuracy = db.Column(db.Float, nullable=False)
    
    graph_definition = [ 
                           [ ('Losses', ['training_loss', 'validation_loss']),
                             ('Accuracy', ['training_accuracy', 'validation_accuracy']) ]
                       ]
    
    actions = {'main': imagenet_classification_train_run}
    
    exclude_from_form = ['graphs',
                         'training_loss','training_accuracy',
                         'validation_loss', 'validation_accuracy',
                         'created_at', 'model_path']
    
    def __init__(self, *args, **kwargs):
        
        super(ImagenetClassification, self).__init__(*args, **kwargs)
        
        self.gpu_id = 0
        self.batch_size = 100
        self.learning_rate = 0.0001
        
        self.created_at = datetime.utcnow
        self.model_path = ''
        
        self.training_loss = 0.0
        self.training_accuracy = 0.0
        self.validation_loss = 0.0
        self.validation_accuracy = 0.0
        
        self.graphs = BaseGraph(self.graph_definition)
    
    def __repr__(self):
        
        return ('<Imagenet classification experiment batch_size={}, learning_rate={}, graphs={}>'.format(
                self.batch_size,
                self.learning_rate,
                self.graphs))

