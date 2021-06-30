from datetime import datetime
import hashlib
import os
import subprocess

import flask
import flask_sqlalchemy
from sqlalchemy import func

UPLOAD_FOLDER = 'files'

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = flask_sqlalchemy.SQLAlchemy(app)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" in flask.session:
            return function(*args, **kwargs)
        else:
            return flask.redirect('/sign-in')

    return wrapper


@app.route('/files/<path:filename>', endpoint='files')
@login_is_required
def files(filename):
    return flask.send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)


@app.context_processor
def global_data():
    def first_name():
        return flask.session.get('first_name', 'Гость')

    def user_type():
        return flask.session.get('user_type', [])

    def version():
        return subprocess.check_output(['git', 'describe']).decode("utf-8")

    return dict(first_name=first_name, user_type=user_type, version=version)


@app.route('/logout')
def logout():
    if 'user_id' in flask.session:
        flask.session.pop('user_id')
    if 'first_name' in flask.session:
        flask.session.pop('first_name')
    if 'user_type' in flask.session:
        flask.session.pop('user_type')

    return flask.redirect('sign-in')


@app.route('/discipline', endpoint='discipline')
@login_is_required
def discipline():
    return flask.render_template('solving.html')


@app.route('/', endpoint='index')
@login_is_required
def index():
    return flask.render_template('index.html')


@app.route('/solving/<int:id_>', endpoint='solving_id', methods=['GET', 'POST'])
@login_is_required
def solving_id(id_):
    solving__ = Solving.query.filter_by(id=id_).first()
    task__ = solving__.student_task.task
    requirement__ = Requirement.query.filter_by(task_id=task__.id).all()

    if flask.request.method == 'POST':
        review__ = Review(review_status_id=1, solving_id=id_)
        if 'teacher' in flask.session['user_type']:
            review__.teacher_id = flask.session['user_id']
        if 'student' in flask.session['user_type']:
            review__.student_id = flask.session['user_id']
        db.session.add(review__)
        db.session.commit()
        for key in flask.request.form:
            if flask.request.form[key]:
                review__.review_status_id = 2
                if 'requirement.' in key:
                    requirement_id = int(key.replace('requirement.', ''))
                    review_comment__ = ReviewComment(review_id=review__.id, requirement_id=requirement_id,
                                                     message=flask.request.form[key])
                    db.session.add(review_comment__)
                if 'common' in key:
                    review__.message = flask.request.form[key]
        solving__.review_count += 1
        if review__.review_status_id == 2:
            solving__.student_task.student_task_status_id = 2
        elif 'teacher' in flask.session['user_type']:
            solving__.student_task.student_task_status_id = 5
        elif solving__.review_count >= solving__.student_task.task.review_count:
            solving__.student_task.student_task_status_id = 4
        db.session.commit()

    task_ = {
        'name': task__.name,
        'text': task__.text,
        'file_path': solving__.file_path + '/' + solving__.file_name,
        'requirement': [],
    }
    for requirement_ in requirement__:
        task_['requirement'].append({
            'id': requirement_.id,
            'text': requirement_.text,
        })
    return flask.render_template('solving_id.html', task=task_)


@app.route('/solving', endpoint='solving')
@login_is_required
def solving():
    if 'student' in flask.session['user_type']:
        tasks_ = []
        query = db.session.query(Solving, func.max(Solving.id).label('id'))
        query = query.join(StudentTask, StudentTask.id == Solving.student_task_id)
        query = query.filter(
            (StudentTask.student_task_status_id == 3) & (StudentTask.student_id.isnot(flask.session['user_id'])))
        query = query.group_by(Solving.student_task_id)
        for solving__, _ in query.all():
            tasks_.append({
                'discipline': solving__.student_task.task.theme.discipline.name,
                'theme': solving__.student_task.task.theme.name,
                'task': solving__.student_task.task.name,
                'status': solving__.student_task.student_task_status.name,
                'id': solving__.id
            })
        return flask.render_template('solving.html', tasks=tasks_)
    if 'teacher' in flask.session['user_type']:
        tasks_ = []
        for solving_ in db.session.query(Solving).join(StudentTask, StudentTask.id == Solving.student_task_id).filter(
                (StudentTask.student_task_status_id == 4)).all():
            tasks_.append({
                'discipline': solving_.student_task.task.theme.discipline.name,
                'theme': solving_.student_task.task.theme.name,
                'task': solving_.student_task.task.name,
                'status': solving_.student_task.student_task_status.name,
                'id': solving_.id
            })
        return flask.render_template('solving.html', tasks=tasks_)


@app.route('/student_task/<int:id_>', endpoint='student_task_id', methods=['POST', 'GET'])
@login_is_required
def student_task_id(id_):
    student_task__ = StudentTask.query.filter_by(id=id_).first()
    if flask.request.method == 'POST':
        if 'zip' in flask.request.files:
            zip_file = flask.request.files['zip']
            if zip_file.filename != '':
                solving__ = Solving(
                    file_path='file_path',
                    file_name='file_name',
                    review_count=0,
                    student_task_id=id_,
                )
                db.session.add(solving__)
                db.session.commit()
                file_path = os.path.join('task', str(solving__.student_task.task.id), 'solving', str(solving__.id))
                full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
                solving__.file_path = file_path
                solving__.file_name = zip_file.filename
                student_task__.student_task_status_id = 3
                db.session.commit()
                if not os.path.exists(full_file_path):
                    os.makedirs(full_file_path)
                zip_file.save(os.path.join(full_file_path, zip_file.filename))

    student_task_ = {
        'id': student_task__.task.id,
        'name': student_task__.task.name,
        'text': student_task__.task.text,
        'count_review': student_task__.task.review_count,
        'load_file': student_task__.student_task_status_id != 5,
        'requirement': [],
        'solving': [],
    }

    for requirement_ in Requirement.query.filter_by(task_id=student_task__.task_id).all():
        student_task_['requirement'].append(requirement_.text)

    for solving_ in Solving.query.filter_by(student_task_id=student_task__.id).all():
        student_task_['solving'].append({
            'file_name': solving_.file_name,
            'file_path': solving_.file_path,
            'review_count': solving_.review_count,
            'created_at': solving_.created_at,
            'review': []
        })
        for review_ in Review.query.filter_by(solving_id=solving_.id).all():
            student_task_['solving'][:1].append({
                'status': review_.review_status.name,
                'id': review_.id,
            })

    return flask.render_template('student_task_id.html', student_task=student_task_)


@app.route('/student_task', endpoint='student_task')
@login_is_required
def student_task():
    student_task_ = []
    for student_task_status in StudentTaskStatus.query.all():
        for student_task__ in StudentTask.query.filter_by(student_id=flask.session['user_id'],
                                                          student_task_status_id=student_task_status.id).all():
            student_task_.append({
                'discipline': student_task__.task.theme.discipline.name,
                'theme': student_task__.task.theme.name,
                'task': student_task__.task.name,
                'status': student_task__.student_task_status.name,
                'id': student_task__.task.id
            })
    return flask.render_template('student_task.html', student_task=student_task_)


@app.route('/sign-in', methods=['POST', 'GET'])
def sign_in():
    if flask.request.method == 'POST':
        try:
            user = User.query.filter_by(email=flask.request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(flask.request.form['password'].encode('utf-8')).hexdigest():
                    flask.session['user_id'] = user.id
                    flask.session['first_name'] = user.first_name
                    flask.session['user_type'] = []
                    if Student.query.filter_by(user_id=user.id).all():
                        flask.session['user_type'].append('student')
                    if Teacher.query.filter_by(user_id=user.id).all():
                        flask.session['user_type'].append('teacher')
                    return flask.redirect('/solving')
                else:
                    return flask.redirect('sign-in?mess=Пароль не верный')
            else:
                return flask.redirect('sign-up?mess=Нет такого пользователя')
        except Exception as ex:
            return flask.redirect(f'sign-in?mess={str(ex)}')
    return flask.render_template('sign-in.html')


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if flask.request.method == 'POST':
        try:
            user = User.query.filter_by(email=flask.request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(flask.request.form['password'].encode('utf-8')).hexdigest():
                    return sign_in()
                return flask.redirect('sign-up?mess=Уже зарегистрирован')
            db.session.add(
                User(
                    email=flask.request.form['email'],
                    password_hash=hashlib.sha1(flask.request.form['password'].encode('utf-8')).hexdigest(),
                    last_name=flask.request.form['last_name'],
                    first_name=flask.request.form['first_name'],
                    middle_name=flask.request.form['middle_name']
                )
            )
            db.session.commit()
            return flask.redirect('/')
        except Exception as ex:
            return flask.redirect(f'sign-up?mess={str(ex)}')
    return flask.render_template('sign-up.html')


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<StudentTaskStatus {self.id}>'


class StudentTask(db.Model):
    __tablename__ = 'StudentTask'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    score = db.Column(db.Integer, default=1)

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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Group {self.id}>'


class StudentStatus(db.Model):
    __tablename__ = 'StudentStatus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<StudentStatus {self.id}>'


class Departament(db.Model):
    __tablename__ = 'Departament'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Departament {self.id}>'


class ReviewStatus(db.Model):
    __tablename__ = 'ReviewStatus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<ReviewStatus {self.id}>'


class Solving(db.Model):
    __tablename__ = 'Solving'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('Teacher.user_id'), nullable=False)
    author = db.relationship("Teacher")

    departament_id = db.Column(db.Integer, db.ForeignKey('Departament.id'), nullable=False)
    departament = db.relationship("Departament")

    def __repr__(self):
        return f'<Discipline {self.id}>'


class Review(db.Model):
    __tablename__ = 'Review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.user_id'))
    teacher = db.relationship("Teacher")

    student_id = db.Column(db.Integer, db.ForeignKey('Student.user_id'))
    student = db.relationship("Student")

    review_status_id = db.Column(db.Integer, db.ForeignKey('ReviewStatus.id'), nullable=False)
    review_status = db.relationship("ReviewStatus")

    solving_id = db.Column(db.Integer, db.ForeignKey('Solving.id'), nullable=False)
    solving = db.relationship("Solving")

    def __repr__(self):
        return f'<Review {self.id}>'


class Theme(db.Model):
    __tablename__ = 'Theme'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)

    discipline_id = db.Column(db.Integer, db.ForeignKey('Discipline.id'), nullable=False)
    discipline = db.relationship("Discipline")

    def __repr__(self):
        return f'<Theme {self.id}>'


class ReviewComment(db.Model):
    __tablename__ = 'ReviewComment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(256), nullable=False)

    review_id = db.Column(db.Integer, db.ForeignKey('Review.id'), nullable=False)
    review = db.relationship("Review")

    requirement_id = db.Column(db.Integer, db.ForeignKey('Requirement.id'), nullable=False)
    requirement = db.relationship("Requirement")

    def __repr__(self):
        return f'<ReviewComment {self.id}>'


class Task(db.Model):
    __tablename__ = 'Task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text(), nullable=False)

    theme_id = db.Column(db.Integer, db.ForeignKey('Theme.id'), nullable=False)
    theme = db.relationship("Theme")

    def __repr__(self):
        return f'<Task {self.id}>'


class Requirement(db.Model):
    __tablename__ = 'Requirement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text(), nullable=False)

    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'), nullable=False)
    task = db.relationship("Task")

    def __repr__(self):
        return f'<Requirement {self.id}>'


if __name__ == '__main__':
    app.run(debug=True)
