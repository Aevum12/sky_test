from flask_login import logout_user
from flask_login import login_required, current_user, login_user
from flask import render_template, request, redirect, url_for, flash, g, jsonify, session
from app.models import User, File, CodeCheckResult
from app.main.utils import is_python_file
from app.main.auth import is_user_authenticated
from app.log_event import add_file_action_log
from app.extensions import db, redis
from app import app


@app.route("/")
def home():
    if g.user_authenticated:
        return redirect(url_for('lk'))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if g.user_authenticated:
        return redirect(url_for('lk'))
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if is_user_authenticated(email, password):
            return redirect(url_for('lk'))

        error_message = "Invalid email or password"

    return render_template("login.html", error_message=error_message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('lk'))
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            validated_email = User.validate_email(email)
            user = User(email=validated_email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)

            return redirect(url_for('lk'))
        except ValueError as e:
            error_message = str(e)

    return render_template('register.html', error_message=error_message)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/lk")
@login_required
def lk():
    try:
        user_main_file = File.query.filter_by(user_id=current_user.id).filter(File.status != 'Deleted').first()
        check_result = []
        if user_main_file:
            check_result = CodeCheckResult.query.filter_by(file_id=user_main_file.id).first()
            if check_result:
                check_result = check_result.get_report()
        user_files = File.query.filter_by(user_id=current_user.id).filter(File.status == 'Deleted').all()
    except Exception as e:
        print(e)
    return render_template(
        "lk.html",
        user_file=user_main_file,
        check_result=check_result,
        user_files=user_files
    )


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    user = current_user

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('lk'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('lk'))

    if not is_python_file(file.filename):
        flash('Only python files are allowed')
        return redirect(url_for('lk'))

    if file:
        # запись файла в бд
        new_file = File(filename=file.filename, status='New', user_id=user.id)
        new_file.set_filename(file.filename)
        new_file.file_data = new_file.serialize(file.read())

        db.session.add(new_file)
        db.session.commit()

        add_file_action_log(new_file.id, 'upload')

        flash('File uploaded successfully')
        return redirect(url_for('lk'))

    return redirect(url_for('lk'))


@app.route("/delete_file")
@login_required
def delete_file():
    user = current_user
    user_file = File.query.filter_by(user_id=user.id).filter(File.status != 'Deleted').first()

    if user_file:
        user_file.status = 'Deleted'
        user_file.file_data = None
        db.session.commit()
        add_file_action_log(user_file.id, 'upload')
        flash('File deleted successfully')
    else:
        flash('No file to delete')

    return redirect(url_for('lk'))


@app.route("/replace_file", methods=['POST'])
@login_required
def replace_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('lk'))

    user = current_user
    user_file = File.query.filter_by(user_id=user.id).filter(File.status != 'Deleted').first()

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('lk'))

    if not is_python_file:
        flash('Only python files are allowed')
        return redirect(url_for('lk'))

    if user_file and file:
        user_file.status = 'Deleted'
        user_file.file_data = None

        new_file = File(filename=file.filename, status='New', user_id=user.id)
        new_file.set_filename(file.filename)
        new_file.file_data = new_file.serialize(file.read())

        db.session.add(new_file)
        db.session.commit()

        add_file_action_log(user_file.id, 'replace')
        flash('File replaced successfully')
    else:
        flash('No file to replace')

    return redirect(url_for('lk'))


@app.route('/get_report/<int:file_id>')
@login_required
def get_report(file_id):
    file = File.query.get_or_404(file_id)
    check_result = CodeCheckResult.query.filter_by(file_id=file_id).first()
    if check_result:
        check_result = check_result.get_report()
    else:
        check_result = None

    return render_template('report.html', check_result=check_result)
