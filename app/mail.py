from flask_mail import Message
from app.extensions import mail, db
from kombu import Exchange, Queue
from app import celery_inst
from app.models import FileActionLog


def send_email(to, subject, body):
    try:
        msg = Message(subject, recipients=[to], body=body)
        mail.send(msg)
    except Exception as e:
        print(e)


@celery_inst.task(queue=Queue('notifications', exchange=Exchange('notifications'), routing_key='notifications'))
def send_notification_email(user_email, file):
    print('email', user_email)
    subject = f"File {file.filename} has been checked"
    body = f"File {file.filename} has been checked."
    send_email(user_email, subject, body)
    event = FileActionLog.query.filter_by(file_id=file.id).first()
    event.email_is_sent = True
    db.session.commit()
