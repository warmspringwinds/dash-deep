from dash_deep.app import db
from dash_deep.plot import BaseGraph
import copy


from dash_deep.scripts.endovis_binary_segmentation_train import run as endovis_binary_segmentation_train_run

class EndovisBinary(db.Model):
    
    title = 'Endovis Binary Segmentation'
    id = db.Column(db.Integer, primary_key=True)
    
    batch_size = db.Column(db.String(80), nullable=False)
    learning_rate = db.Column(db.String(120), nullable=False)
    output_stride = db.Column(db.String(120), nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    actions = {'main': endovis_binary_segmentation_train_run}
    
    exclude_from_form = ['graphs']
    
    def __init__(self, *args, **kwargs):
        
        super(EndovisBinary, self).__init__(*args, **kwargs)
        
        self.batch_size = 100
        self.learning_rate = 0.0001
        self.output_stride = 8
        self.graphs = BaseGraph()
    
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
    
    batch_size = db.Column(db.Integer, nullable=False)
    learning_rate = db.Column(db.Float, nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    actions = {'main': imagenet_classification_train_run}
    
    exclude_from_form = ['graphs']
    
    def __init__(self, *args, **kwargs):
        
        super(ImagenetClassification, self).__init__(*args, **kwargs)
        
        self.batch_size = 100
        self.learning_rate = 0.0001
        self.graphs = BaseGraph()
    
    def __repr__(self):
        
        return ('<Imagenet classification experiment batch_size={}, learning_rate={}, graphs={}>'.format(
                self.batch_size,
                self.learning_rate,
                self.graphs))

