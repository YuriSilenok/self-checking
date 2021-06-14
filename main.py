from flask import Flask, render_template, session, redirect, request
from datetime import datetime
from hashlib import md5

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect('sign-up.html')
        else:
            return function()

    return wrapper


@app.route('/')
@login_is_required
def index():
    return render_template('index.html')


@app.route('/sign-up.html', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        try:
            users = User.query.select(email=request.form['email'])
            if len(users) > 0:
                return redirect('sign-up.html')
            user = User(
                email=request.form['email'],
                password_hash=md5(request.form['password1']),

            )
        except:
            pass
    else:
        return render_template('sign-up.html')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(32), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    surname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.id}>'


if __name__ == '__main__':
    app.run(debug=True)
