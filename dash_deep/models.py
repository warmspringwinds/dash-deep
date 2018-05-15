from dash_deep.app import db
from dash_deep.scripts.semantic_segmentation_train_script import run


class PascalSegmentation(db.Model):
    
    title = 'Pascal Semantic Segmentation Experiment'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_size = db.Column(db.String(80), nullable=False)
    learning_rate = db.Column(db.String(120), nullable=False)
    output_stride = db.Column(db.String(120), nullable=False)
    
    actions = {'main': run}
    
    def __repr__(self):
        
        return '<Pascal Image Segmentation experiment>'

    
class ImagenetClassification(db.Model):
    
    title = 'Imagenet Classification Experiment' 
    
    id = db.Column(db.Integer, primary_key=True)
    batch_size = db.Column(db.String(80), unique=True, nullable=False)
    learning_rate = db.Column(db.String(120), unique=True, nullable=False)
    
    actions = {'main': lambda x: x}

    def __repr__(self):
        
        return '<Imagenet classification experiment>'

