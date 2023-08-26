import os
import secrets
from kombu import Exchange, Queue

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = secrets.token_hex(16)
    # sqlite
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') \
    #                           or 'sqlite:///' + os.path.join(basedir, 'database.sqlite?charset=utf8')

    # docker postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') \
                              or 'postgresql://postgres_root:asdf234Kj786o@db:5432/sky_db?client_encoding=utf8'

    REDIS_URL = os.environ.get('REDIS_URI') or "redis://redis:6379/0"
    CELERY = {
        'CELERY_BROKER_URL': os.environ.get('CELERY_BROKER_URL') or 'redis://redis:6379/0',
        'CELERY_RESULT_BACKEND': os.environ.get('CELERY_RESULT_BACKEND') or 'redis://redis:6379/0',
        'CELERY_LOG_LEVEL': 'DEBUG',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True

    # specify mail server
    MAIL_SERVER = 'smtp.rambler.ru'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'login'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = 'login@rambler.ru'
