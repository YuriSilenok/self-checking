from flask import Flask, render_template, session, redirect, request
from datetime import datetime
import hashlib

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect('sign-in')
        else:
            return function()

    return wrapper


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
    text = db.Column(db.Text(), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

    theme = db.relationship("Theme")

    def __repr__(self):
        return f'<Task {self.id}>'


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
