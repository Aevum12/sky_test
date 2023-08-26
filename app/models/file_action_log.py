from app.extensions import db
from datetime import datetime


class FileActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    email_is_sent = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
