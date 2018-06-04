from dash_deep.app import db


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
    
    def __repr__(self):
        
        return ('<Endovis Binary Segmentation experiment batch_size={}, learning_rate={}>, output_stride={}'.format(
                self.batch_size,
                self.learning_rate,
                self.output_stride))


from dash_deep.scripts.imagenet_classification_train import run as imagenet_classification_train_run
    
class ImagenetClassification(db.Model):
    
    title = 'Imagenet Classification'
    id = db.Column(db.Integer, primary_key=True)
    
    batch_size = db.Column(db.String(80), unique=True, nullable=False)
    learning_rate = db.Column(db.String(120), unique=True, nullable=False)
    
    graphs = db.Column(db.PickleType())
    
    actions = {'main': imagenet_classification_train_run}
    
    exclude_from_form = ['graphs']
    
    def __repr__(self):
        
        return ('<Imagenet classification experiment batch_size={}, learning_rate={}>'.format(
                self.batch_size,
                self.learning_rate))

