from app.models import FileActionLog
from app.extensions import db


def add_file_action_log(file_id, action_type):
    log_entry = FileActionLog(file_id=file_id, action_type=action_type)
    db.session.add(log_entry)
    db.session.commit()
