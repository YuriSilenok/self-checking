from flask import Flask, render_template, session, redirect, request, url_for, send_file
from datetime import datetime
import hashlib
import os

from flask_sqlalchemy import SQLAlchemy

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


@app.route('/review', endpoint='review', methods=['POST', 'GET'])
@login_is_required
def review():
    if request.method == 'GET':
        if 'solving' in request.args:
            return render_template('solving-review.html')


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


@app.route('/solving', endpoint='solving', methods=['POST', 'GET'])
@login_is_required
def solving():
    task = Task.query.filter_by(id=request.args['task']).first()
    data = []
    if request.method == 'POST':
        if 'zip' not in request.files:
            return render_template('solving.html')
        zip_file = request.files['zip']
        if zip_file.filename == '':
            return render_template('solving.html')
        db.session.add(Solving(
            file_path='file_path',
            file_name='file_name',
            review_count=0,
            task_id=task.id
        ))
        db.session.commit()
        solving_row = Solving.query.filter_by(file_path='file_path', file_name='file_name', task_id=task.id).first()
        file_path = os.path.join('task', str(task.id), 'solving', str(solving_row.id))
        full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
        solving_row.file_path = file_path
        solving_row.file_name = zip_file.filename
        db.session.commit()
        if not os.path.exists(full_file_path):
            os.makedirs(full_file_path)
        zip_file.save(os.path.join(full_file_path, zip_file.filename))
    for solving_row in Solving.query.filter_by(task_id=task.id).all():
        solving_row = {
            'created_at': solving_row.created_at,
            'file_path': solving_row.file_path,
            'file_name': solving_row.file_name,
            'review_count': solving_row.review_count,
            'href': url_for(UPLOAD_FOLDER,
                            filename=os.path.join(solving_row.file_path, solving_row.file_name)).replace('%5C', '/'),
        }
        solving_comments = []
        for solving_comment in ReviewComment.query.filter_by(solving_id=solving_row.id):
            solving_comments.append({
                'created_at': solving_row.created_at,
                'message': solving_comment.message,
            })
        solving_row['solving_comments'] = solving_comments
        data.append(solving_row)
    return render_template('solvings.html', data=data)


@app.route('/to-do', endpoint='to_do')
@login_is_required
def to_do():
    task_data = {}
    if 'task' in request.args:
        task = Task.query.filter_by(id=request.args['task']).first()
        task_data = {
            'id': task.id,
            'discipline': task.theme.discipline.name,
            'theme': task.theme.name,
            'name': task.name,
            'text': task.text,
        }
        requirements = []
        for task_requirement in Requirement.query.filter_by(task_id=request.args['task']).all():
            requirements.append({
                'text': task_requirement.text
            })
        task_data['requirements'] = requirements

    task_reject = task_todo = task_wait = task_done = tasks = []
    for user_task in StudentTask.query.filter_by(student_id=session['user_id']):
        tasks.append({
            'id': user_task.task.id,
            'discipline': user_task.task.theme.discipline.name,
            'theme': user_task.task.theme.name,
            'name': user_task.task.name,
        })

    return render_template('to-do.html', tasks=tasks, task_data=task_data)


@app.route('/task/<int:id_>', endpoint='my_task')
@login_is_required
def task(id_):
    task_ = Task.query.filter_by(id=id_).first()
    task_ = {
        'id': task_.id,
        'name': task_.name,
        'text': task_.text,
        'count_review': task_.review_count,
        'solving': [],
    }
    student_task_ = StudentTask.query.filter_by(task_id=task_['id']).first()

    for solving_ in Solving.query.filter_by(student_task_id=student_task_.id).all():
        task_['solving'].append({
            'file_name': solving_.file_name,
            'file_path': solving_.file_path,
            'review_count': solving_.review_count,
            'created_at': solving_.created_at,
        })
    return render_template('task.html', task=task_)


@app.route('/my-works', endpoint='my_works')
@login_is_required
def my_works():
    tasks = []
    for student_task_status in StudentTaskStatus.query.all():
        for student_task in StudentTask.query.filter_by(student_id=session['user_id'],
                                                        student_task_status_id=student_task_status.id).all():
            tasks.append({
                'discipline': student_task.task.theme.discipline.name,
                'theme': student_task.task.theme.name,
                'task': student_task.task.name,
                'status': student_task.student_task_status.name,
                'id': student_task.task.id
            })
    return render_template('my-works.html', tasks=tasks)


@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    session['user_id'] = user.id
                    session['user_name'] = user.first_name
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
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.id}>'


class Student(db.Model):
    __tablename__ = 'Student'

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    user = db.relationship("User")

    group_id = db.Column(db.Integer, db.ForeignKey('Group.id'), nullable=False)
    group = db.relationship("Group")

    student_status_id = db.Column(db.Integer, db.ForeignKey('StudentStatus.id'), nullable=False)
    student_status = db.relationship("StudentStatus")

    def __repr__(self):
        return f'<Student {self.user_id}>'


class Teacher(db.Model):
    __tablename__ = 'Teacher'

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    user = db.relationship("User")

    departament_id = db.Column(db.Integer, db.ForeignKey('Departament.id'), nullable=False)
    departament = db.relationship("Departament")

    def __repr__(self):
        return f'<Teacher {self.user_id}>'


class StudentTaskStatus(db.Model):
    __tablename__ = 'StudentTaskStatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<StudentTaskStatus {self.id}>'


class StudentTask(db.Model):
    __tablename__ = 'StudentTask'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    student_task_status_id = db.Column(db.Integer, db.ForeignKey('StudentTaskStatus.id'), default=1, nullable=False)
    student_task_status = db.relationship('StudentTaskStatus')

    student_id = db.Column(db.Integer, db.ForeignKey('Student.user_id'), nullable=False)
    student = db.relationship('Student')

    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'), nullable=False)
    task = db.relationship('Task')

    def __repr__(self):
        return f'<StudentTask {self.id}>'


class Group(db.Model):
    __tablename__ = 'Group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Group {self.id}>'


class StudentStatus(db.Model):
    __tablename__ = 'StudentStatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<StudentStatus {self.id}>'


class Departament(db.Model):
    __tablename__ = 'Departament'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Departament {self.id}>'


class ReviewStatus(db.Model):
    __tablename__ = 'ReviewStatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<ReviewStatus {self.id}>'


class Solving(db.Model):
    __tablename__ = 'Solving'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    review_count = db.Column(db.Integer, nullable=False)

    student_task_id = db.Column(db.Integer, db.ForeignKey('StudentTask.id'), nullable=False)
    student_task = db.relationship("StudentTask")

    def __repr__(self):
        return f'<Solving {self.id}>'


class Discipline(db.Model):
    __tablename__ = 'Discipline'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('Teacher.user_id'), nullable=False)
    author = db.relationship("Teacher")

    departament_id = db.Column(db.Integer, db.ForeignKey('Departament.id'), nullable=False)
    departament = db.relationship("Departament")

    def __repr__(self):
        return f'<Discipline {self.id}>'


class Review(db.Model):
    __tablename__ = 'Review'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.user_id'))
    teacher = db.relationship("Teacher")

    student_id = db.Column(db.Integer, db.ForeignKey('Student.user_id'))
    student = db.relationship("Student")

    status_id = db.Column(db.Integer, db.ForeignKey('ReviewStatus.id'), nullable=False)
    status = db.relationship("ReviewStatus")

    solving_id = db.Column(db.Integer, db.ForeignKey('Solving.id'), nullable=False)
    solving = db.relationship("Solving")

    def __repr__(self):
        return f'<Review {self.id}>'


class Theme(db.Model):
    __tablename__ = 'Theme'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    discipline_id = db.Column(db.Integer, db.ForeignKey('Discipline.id'), nullable=False)
    discipline = db.relationship("Discipline")

    def __repr__(self):
        return f'<Theme {self.id}>'


class ReviewComment(db.Model):
    __tablename__ = 'ReviewComment'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(256), nullable=False)

    review_id = db.Column(db.Integer, db.ForeignKey('Review.id'), nullable=False)
    review = db.relationship("Review")

    requirement_id = db.Column(db.Integer, db.ForeignKey('Requirement.id'), nullable=False)
    requirement = db.relationship("Requirement")

    def __repr__(self):
        return f'<ReviewComment {self.id}>'


class Task(db.Model):
    __tablename__ = 'Task'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text(), nullable=False)

    theme_id = db.Column(db.Integer, db.ForeignKey('Theme.id'), nullable=False)
    theme = db.relationship("Theme")

    def __repr__(self):
        return f'<Task {self.id}>'


class Requirement(db.Model):
    __tablename__ = 'Requirement'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)

    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'), nullable=False)
    task = db.relationship("Task")

    def __repr__(self):
        return f'<Requirement {self.id}>'


if __name__ == '__main__':
    app.run(debug=True)
