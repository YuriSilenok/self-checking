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
            return redirect('sign-in.html')
        else:
            return function()

    return wrapper


@app.route('/logout.html')
def logout():
    session.pop('user_id')
    session.pop('user_name')
    return redirect('sign-in.html')


@app.route('/')
@login_is_required
def index():
    return render_template('index.html')


@app.route('/sign-in.html', methods=['POST', 'GET'])
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
                    return redirect('sign-in.html?mess=Пароль не верный')
            else:
                return redirect('sign-up.html?mess=Нет такого пользователя')
        except Exception as ex:
            return redirect(f'sign-in.html?mess={str(ex)}')
    return render_template('sign-in.html')


@app.route('/sign-up.html', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    session['user_id'] = user.id
                    session['user_name'] = user.name
                    return redirect('/')
                return redirect('sign-up.html?mess=Уже зарегистрирован')
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
            return redirect(f'sign-up.html?mess={str(ex)}')
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
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))

    discipline = db.relationship("Discipline")

    def __repr__(self):
        return f'<Theme {self.id}>'


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))

    theme = db.relationship("Theme")

    def __repr__(self):
        return f'<Task {self.id}>'


class DisciplineStatus(db.Model):
    __tablename__ = 'discipline_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Discipline status {self.id}>'


class UserDiscipline(db.Model):
    __tablename__ = 'user_discipline'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discipline_id = db.Column(db.Integer, db.ForeignKey('discipline.id'))
    discipline_status_id = db.Column(db.Integer, db.ForeignKey('discipline_status.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
    discipline = db.relationship("Discipline")
    discipline_status = db.relationship("DisciplineStatus")

    def __repr__(self):
        return f'<User_Discipline {self.user_id} {self.discipline_id}>'


if __name__ == '__main__':
    app.run(debug=True)
