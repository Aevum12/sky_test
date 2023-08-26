import tempfile
import subprocess
import os
import json
from kombu import Exchange, Queue
from app.models import File, CodeCheckResult, User
from app.extensions import db
from app import celery_inst
from app.mail import send_notification_email


@celery_inst.task(queue=Queue('default', exchange=Exchange('default'), routing_key='default'))
def launch_script_check(file_id, user_email):
    try:
        user_file = File.query.filter_by(id=file_id).filter(File.status != 'Deleted').first()
        py_file = File.deserialize(user_file.file_data)

        report = script_check(py_file, user_file.filename)
        print(report)

        # запись отчета в бд
        new_report = CodeCheckResult(file_id=file_id)
        new_report.set_report(report)
        user_file.status = 'Checked'
        db.session.add(new_report)
        db.session.commit()
        send_notification_email.delay(user_email, user_file)
    except Exception as e:
        print(e)


def script_check(file_content, file_name):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        result = subprocess.run(
            ['pylint', '--disable=', '--msg-template="{path}:{line}:{column} - {msg} ({msg_id})"',
             '--output-format=colorized', '--output-format=json', temp_file_path],
            capture_output=True,
            text=True
        )
        pylint_report = json.loads(result.stdout)
        for issue in pylint_report:
            issue['path'] = file_name
        return pylint_report

    finally:
        if temp_file_path:
            try:
                os.remove(temp_file_path)
            except:
                pass


@celery_inst.task(queue=Queue('checks', exchange=Exchange('checks'), routing_key='checks'))
def process_new_files():
    print('process_new_files')
    new_files = File.query.filter_by(status='New').all()
    for new_file in new_files:
        user = User.query.get(new_file.user_id)
        if user is not None:
            launch_script_check.delay(new_file.id, user.email)
            new_file.status = 'Processing'
            db.session.commit()
