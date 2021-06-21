from flask import Flask, render_template, session, redirect, request, url_for, send_file
from datetime import datetime
import hashlib
import os

from flask_sqlalchemy import SQLAlchemy

# UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files')
# UPLOAD_FOLDER = os.path.join('.', 'files')
UPLOAD_FOLDER = 'files'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect('sign-in')
        else:
            return function(*args, **kwargs)

    return wrapper


@app.route('/files/<path:filename>', endpoint='files')
@login_is_required
def files(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename.replace('/', '\\')), as_attachment=True)


@app.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('user_name')
    return redirect('sign-in')


@app.route('/', endpoint='index')
@login_is_required
def index():
    return render_template('index.html')


@app.route('/my-works', endpoint='my_works')
@login_is_required
def my_works():
    return render_template('my-works.html')


@app.route('/review', endpoint='review', methods=['POST', 'GET'])
@login_is_required
def review():
    if request.method == 'GET':
        if 'solving' in request.args:
            render_template('solving-review.html')


@app.route('/horizontal-review', endpoint='horizontal_review')
@login_is_required
def horizontal_review():
    data = []
    query = db.session.query(Solving, Task)
    query = query.join(Solving, Solving.task_id == Task.id)
    query = query.filter(Solving.review_count < Task.review_count)
    for row in query.all():
        solving = row.Solving
        data.append({
            'solving_id': solving.id,
            'solving_file_name': solving.file_name,
            'solving_created_at': solving.created_at,
            'solving_review_count': solving.review_count,
            'task_review_count': solving.task.review_count,
            'task_name': solving.task.name,
        })
    return render_template('horizontal-review.html', data=data)


@app.route('/solvings', endpoint='solvings', methods=['POST', 'GET'])
@login_is_required
def solvings():
    task = Task.query.filter_by(id=request.args['task']).first()
    data = []
    if request.method == 'POST':
        if 'zip' not in request.files:
            return render_template('solvings.html')
        zip_file = request.files['zip']
        if zip_file.filename == '':
            return render_template('solvings.html')
        db.session.add(Solving(
            file_path='file_path',
            file_name='file_name',
            review_count=0,
            task_id=task.id
        ))
        db.session.commit()
        solving = Solving.query.filter_by(file_path='file_path', file_name='file_name', task_id=task.id).first()
        file_path = os.path.join('task', str(task.id), 'solving', str(solving.id))
        full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
        solving.file_path = file_path
        solving.file_name = zip_file.filename
        db.session.commit()
        if not os.path.exists(full_file_path):
            os.makedirs(full_file_path)
        zip_file.save(os.path.join(full_file_path, zip_file.filename))
    for solving in Solving.query.filter_by(task_id=task.id).all():
        solving_row = {
            'created_at': solving.created_at,
            'file_path': solving.file_path,
            'file_name': solving.file_name,
            'review_count': solving.review_count,
            'href': url_for(UPLOAD_FOLDER,
                            filename=os.path.join(solving.file_path, solving.file_name)).replace('%5C', '/'),
        }
        solving_comments = []
        for solving_comment in SolvingComment.query.filter_by(solving_id=solving.id):
            solving_comments.append({
                'created_at': solving.created_at,
                'message': solving_comment.message,
            })
        solving_row['solving_comments'] = solving_comments
        data.append(solving_row)
    return render_template('solvings.html', data=data)


@app.route('/to-do', endpoint='to_do')
@login_is_required
def to_do():
    user_tasks = UserTask.query.filter_by(
        user_id=session['user_id'],
        status_id=TaskStatus.query.filter_by(name='Не начата').first().id,
    ).all()
    tasks = []
    for user_task in user_tasks:
        tasks.append({
            'id': user_task.task.id,
            'discipline': user_task.task.theme.discipline.name,
            'theme': user_task.task.theme.name,
            'name': user_task.task.name,
            'text': user_task.task.text
        })
    return render_template(
        'to-do.html',
        tasks=tasks
    )


@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    session['user_id'] = user.id
                    session['user_name'] = user.name
                    return redirect('/')
                else:
                    return redirect('sign-in?mess=Пароль не верный')
            else:
                return redirect('sign-up?mess=Нет такого пользователя')
        except Exception as ex:
            return redirect(f'sign-in?mess={str(ex)}')
    return render_template('sign-in.html')


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    session['user_id'] = user.id
                    session['user_name'] = user.name
                    return redirect('/')
                return redirect('sign-up?mess=Уже зарегистрирован')
            db.session.add(
                User(
                    email=request.form['email'],
                    password_hash=hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest(),
                    surname=request.form['surname'],
                    name=request.form['name'],
                    middle_name=request.form['middle_name']
                )
            )
            db.session.commit()
            return redirect('/')
        except Exception as ex:
            return redirect(f'sign-up?mess={str(ex)}')
    return render_template('sign-up.html')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    surname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.id}>'


class Discipline(db.Model):
    __tablename__ = 'discipline'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<Discipline {self.id}>'


class Theme(db.Model):
    __tablename__ = 'theme'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'), nullable=False)

    discipline = db.relationship("Discipline")

    def __repr__(self):
        return f'<Theme {self.id}>'


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text(), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

    theme = db.relationship("Theme")

    def __repr__(self):
        return f'<Task {self.id}>'


class SolvingComment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    solving_id = db.Column(db.Integer, db.ForeignKey('solving.id'), nullable=False)

    user = db.relationship("User")
    solving = db.relationship("Solving")

    def __repr__(self):
        return f'<Comment {self.id}>'


class TaskRequirement(db.Model):
    __tablename__ = 'task_requirement'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    task = db.relationship("Task")

    def __repr__(self):
        return f'<TaskRequirement {self.id}>'


class TaskRequirementResolutionComment(db.Model):
    __tablename__ = 'task_requirement_resolution_comment'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(256), nullable=False)
    task_requirement_id = db.Column(db.Integer, db.ForeignKey('task_requirement.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship("User")
    task_requirement = db.relationship("task_requirement")

    def __repr__(self):
        return f'<TaskRequirementResolutionComment {self.id}>'


class Solving(db.Model):
    __tablename__ = 'solving'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    task = db.relationship("Task")

    def __repr__(self):
        return f'<Solving {self.id}>'


class TaskStatus(db.Model):
    __tablename__ = 'task_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(11), nullable=False)

    def __repr__(self):
        return f'<Task status {self.id}>'


class UserTask(db.Model):
    __tablename__ = 'user_task'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('task_status.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
    task = db.relationship("Task")
    task_status = db.relationship("TaskStatus")

    def __repr__(self):
        return f'<User_Discipline {self.user_id} {self.discipline_id}>'


if __name__ == '__main__':
    app.run(debug=True)
