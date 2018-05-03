from dash_deep.app import db
from time import sleep


class PascalSegmentation(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    batch_size = db.Column(db.String(80), nullable=False)
    learning_rate = db.Column(db.String(120), nullable=False)
    output_stride = db.Column(db.String(120), nullable=False)
    
    actions = {}
    
    def __repr__(self):
        return '<Pascal Image Segmentation experiment>'


def run(populated_object):
    
    db.engine.dispose()
    
    # Simulate training
    sleep(7)
    
    populated_object.batch_size = '555'
    populated_object.learning_rate = '100'
    populated_object.output_stride = '777'
    
    db.session.add(populated_object)
    db.session.commit()
    
    return 'success'

PascalSegmentation.actions['main'] = run