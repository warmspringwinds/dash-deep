from dash_deep.app import db
from dash_deep.mixins import BasicExperimentMixin


from dash_deep.scripts.endovis_binary_segmentation_train import run as endovis_binary_segmentation_train_run
from dash_deep.scripts.endovis_binary_segmentation_train import inference as endovis_binary_segmentation_inference


class EndovisBinary(BasicExperimentMixin, db.Model):
    
    title = 'Endovis Binary Segmentation'
    output_stride = db.Column(db.Integer, nullable=False)
    
    actions = {'main': endovis_binary_segmentation_train_run,
               'inference': endovis_binary_segmentation_inference}
    
    
    
    def __init__(self, *args, **kwargs):
        
        super(EndovisBinary, self).__init__(*args, **kwargs)
        self.output_stride = 8
        
        
    def __repr__(self):
        
        return ('<Endovis Binary Segmentation experiment id={}, batch_size={}, learning_rate={}>, output_stride={}'.format(
                self.id,
                self.batch_size,
                self.learning_rate,
                self.output_stride))


from dash_deep.scripts.imagenet_classification_train import run as imagenet_classification_train_run


class ImagenetClassification(BasicExperimentMixin, db.Model):
    
    title = 'Imagenet Classification'
    
    actions = {'main': imagenet_classification_train_run}
    
    
    def __init__(self, *args, **kwargs):
        
        super(ImagenetClassification, self).__init__(*args, **kwargs)
        
        
    def __repr__(self):
        
        return ('<Imagenet classification experiment batch_size={}, learning_rate={}, graphs={}>'.format(
                self.batch_size,
                self.learning_rate))

