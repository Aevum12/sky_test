from app.extensions import db
from datetime import datetime
import json


class CodeCheckResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    report = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notification_sent = db.Column(db.Boolean, default=False)

    def set_report(self, report_dict):
        self.report = json.dumps(report_dict)

    def get_report(self):
        return json.loads(self.report) if self.report else None

    def __repr__(self):
        return f'<CodeCheckResult for File {self.file_id} at {self.timestamp}>'
