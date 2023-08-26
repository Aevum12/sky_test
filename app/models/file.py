from app.extensions import db
from sqlalchemy import LargeBinary
from werkzeug.utils import secure_filename
import pickle


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_data = db.Column(LargeBinary, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    actions = db.relationship('FileActionLog', backref='file', lazy=True)

    def set_filename(self, filename):
        self.filename = secure_filename(filename)

    @staticmethod
    def serialize(data):
        return pickle.dumps(data)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)
