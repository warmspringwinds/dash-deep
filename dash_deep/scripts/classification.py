from dash_deep.app import db


class ImagenetClassification(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    batch_size = db.Column(db.String(80), unique=True, nullable=False)
    learning_rate = db.Column(db.String(120), unique=True, nullable=False)
    
    actions = {'main': lambda x: x}

    def __repr__(self):
        return '<Imagenet classification experiment>'