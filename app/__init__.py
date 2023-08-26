from app.extensions import db, redis, mail
from app.models import *
from config import Config
from flask import Flask, g
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from celery import Celery, Task
from celery.schedules import crontab
from kombu import Exchange, Queue
import os


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    CELERY = {
        'CELERY_BROKER_URL': os.environ.get('CELERY_BROKER_URL') or 'redis://redis:6379/0',
        'CELERY_RESULT_BACKEND': os.environ.get('CELERY_RESULT_BACKEND') or 'redis://redis:6379/0',
        'CELERY_IMPORTS': (
            'app.script_check',
        ),
        'CELERYBEAT_SCHEDULE': {
            'process-queue-every-minute': {
                'task': 'app.script_check.process_new_files',
                # 'schedule': crontab(minute='*/1'),
                'schedule': 10.0,
                'args': ()
            },
        },
        'CELERY_QUEUES': (
            Queue('default', Exchange('default'), routing_key='default'),
            Queue('checks', Exchange('checks'), routing_key='checks'),
            Queue('notifications', Exchange('notifications'), routing_key='notifications'),
        ),

    }

    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,

    )

    celery_app.config_from_object(CELERY)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)

    # Register login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Register redis
    redis.init_app(app)

    # Register Celery
    celery_init_app(app)

    # Register mail
    mail.init_app(app)

    @app.before_request
    def before_request():
        g.user_authenticated = current_user.is_authenticated

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


app = create_app()
celery_inst = celery_init_app(app)

from app.main import routes
