from dash_deep.app import db


class PascalSegmentation(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    batch_size = db.Column(db.String(80), unique=True, nullable=False)
    learning_rate = db.Column(db.String(120), unique=True, nullable=False)
    output_stride = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Pascal Image Segmentation experiment>'