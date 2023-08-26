from app.models import User
from functools import wraps
from flask import session, redirect, url_for
from flask_login import login_user


def is_user_authenticated(email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return user
    except Exception as e:
        print(e)
        return None


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return view_func(*args, **kwargs)

    return wrapped_view
