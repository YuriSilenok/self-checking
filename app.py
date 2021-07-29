#!/usr/bin/python
# coding=utf-8

from datetime import datetime
import hashlib
import os
import subprocess

from flask import redirect, request, send_file, render_template, session, url_for, Flask, send_from_directory, jsonify

import flask_sqlalchemy
from sqlalchemy import func

UPLOAD_FOLDER = 'files'

app = Flask('app')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = flask_sqlalchemy.SQLAlchemy(app)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return function(*args, **kwargs)
        else:
            return redirect('/sign-in')

    return wrapper


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/files/<path:filename>', endpoint='files')
@login_is_required
def files(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)


@app.context_processor
def global_data():
    def first_name():
        return session.get('first_name', 'Гость')

    def user_type():
        return session.get('user_type', [])

    def version():
        return subprocess.check_output(['git', 'describe']).decode("utf-8")

    return dict(first_name=first_name, user_type=user_type, version=version)


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    if 'first_name' in session:
        session.pop('first_name')
    if 'user_type' in session:
        session.pop('user_type')

    return redirect('sign-in')


@app.route('/discipline', endpoint='discipline', methods=['POST', 'GET'])
@login_is_required
def discipline():
    if request.method == 'POST':
        discipline__ = Discipline(
            author_id=session['user_id'],
            name=request.form['name'],
            departament_id=Teacher.query.filter_by(user_id=session['user_id']).first().departament_id
        )
        db.session.add(discipline__)
        db.session.commit()
        return redirect(url_for('theme', discipline=discipline__.id))
    data = []
    for discipline__ in Discipline.query.filter_by(author_id=session['user_id']):
        data.append({
            'id': discipline__.id,
            'name': discipline__.name,
        })
    return render_template('discipline.html', data=data)


@app.route('/theme', endpoint='theme', methods=['GET', 'POST'])
@login_is_required
def theme():
    if request.method == 'POST':
        theme__ = Theme(name=request.form['name'], discipline_id=request.args['discipline'])
        db.session.add(theme__)
        db.session.commit()
        return redirect(url_for('task', theme=theme__.id))
    discipline__ = Discipline.query.filter_by(id=request.args['discipline']).first()
    if not discipline__:
        return redirect(url_for('discipline'))
    themes = []
    for theme__ in Theme.query.filter_by(discipline_id=discipline__.id):
        themes.append({
            'id': theme__.id,
            'name': theme__.name,
        })
    discipline_ = {'name': discipline__.name, 'id': discipline__.id}
    return render_template('theme.html', themes=themes, discipline=discipline_, groups=api_group(),
                           students=api_student())


@app.route('/task', endpoint='task', methods=['GET', 'POST'])
@login_is_required
def task():
    if request.method == 'POST':
        task__ = Task(name=request.form['name'], link=request.form['link'],
                      review_count=int(request.form['review_count']), theme_id=request.args['theme'])
        db.session.add(task__)
        db.session.commit()
        return redirect(url_for('requirement', task=task__.id))
    theme__ = Theme.query.filter_by(id=request.args['theme']).first()
    if not theme__:
        return redirect(url_for('theme'))
    data = []
    for task__ in Task.query.filter_by(theme_id=theme__.id):
        data.append({
            'id': task__.id,
            'name': task__.name,
            'link': task__.link,
            'review_count': task__.review_count,
        })
    return render_template('task.html', data=data, theme=theme__.name)


@app.route('/requirement', endpoint='requirement', methods=['GET', 'POST'])
@login_is_required
def requirement():
    if request.method == 'POST':
        requirement__ = Requirement(text=request.form['text'], task_id=request.args['task'])
        db.session.add(requirement__)
        db.session.commit()
    task__ = Task.query.filter_by(id=request.args['task']).first()
    if not task__:
        return redirect(url_for('task'))
    data = []
    for requirement__ in Requirement.query.filter_by(task_id=task__.id):
        data.append({
            'text': requirement__.text,
        })
    return render_template('requirement.html', data=data, task=task__.name)


@app.route('/solving/<int:id_>', endpoint='solving_id', methods=['GET', 'POST'])
@login_is_required
def solving_id(id_):
    solving__ = Solving.query.filter_by(id=id_).first()
    task__ = solving__.student_task.task
    requirement__ = Requirement.query.filter_by(task_id=task__.id).all()

    if request.method == 'POST':
        review__ = Review(solving_id=id_)
        if 'teacher' in session['user_type']:
            review__.teacher_id = session['user_id']
        if 'student' in session['user_type']:
            review__.student_id = session['user_id']
        db.session.add(review__)
        db.session.commit()
        for key in request.form:
            if request.form[key]:
                review__.review_status_id = 2

                if 'requirement.' in key:
                    requirement_id = int(key.replace('requirement.', ''))
                    review_comment__ = ReviewComment(review_id=review__.id, requirement_id=requirement_id,
                                                     message=request.form[key])
                    db.session.add(review_comment__)
            if 'common' in key:
                review__.message = request.form[key]
        solving__.review_count += 1
        if review__.review_status_id == 2:
            solving__.student_task.student_task_status_id = 2
        elif 'teacher' in session['user_type']:
            solving__.student_task.student_task_status_id = 5
        elif solving__.review_count >= solving__.student_task.task.review_count:
            solving__.student_task.student_task_status_id = 4
        db.session.commit()
        return redirect(url_for('solving'))
    task_ = {
        'name': task__.name,
        'link': task__.link,
        'file_path': solving__.file_path + '/' + solving__.file_name,
        'requirement': [],
    }
    for requirement_ in requirement__:
        task_['requirement'].append({
            'id': requirement_.id,
            'text': requirement_.text,
        })
    return render_template('solving_id.html', task=task_)


@app.route('/solving', endpoint='solving')
@app.route('/')
@login_is_required
def solving():
    if 'student' in session['user_type']:
        tasks_ = []
        my_st__ = db.session.query(StudentTask) \
            .where((StudentTask.student_id == session['user_id']) & (StudentTask.student_task_status_id != 5)) \
            .subquery('t')
        st__ = db.session.query(StudentTask, Solving, func.max(Solving.id)) \
            .join(Solving, Solving.student_task_id == StudentTask.id) \
            .join(Review, Review.solving_id == Solving.id, isouter=True) \
            .join(my_st__, my_st__.c.task_id == StudentTask.task_id) \
            .where((StudentTask.student_task_status_id == 3) & (StudentTask.student_id != session['user_id'])) \
            .group_by(StudentTask.id)

        for st__ in st__.all():
            not_my = True
            for r__ in db.session.query(Review).where(st__[1].id == Review.solving_id).all():
                if r__.student.user.id == session['user_id']:
                    not_my = False
                    break
            if not_my:
                tasks_.append({
                    'discipline': st__[0].task.theme.discipline.name,
                    'theme': st__[0].task.theme.name,
                    'task': st__[0].task.name,
                    'status': st__[0].student_task_status.name,
                    'id': st__[1].id,
                })
        return render_template('solving.html', tasks=tasks_)
    if 'teacher' in session['user_type']:
        tasks_ = []

        query__ = db.session.query(Solving)
        query__ = query__.join(StudentTask, Solving.student_task_id == StudentTask.id)
        query__ = query__.where(StudentTask.student_task_status_id == 4)
        query__ = query__.group_by(Solving.student_task_id)

        for solving__ in query__.all():
            tasks_.append({
                'discipline': solving__.student_task.task.theme.discipline.name,
                'theme': solving__.student_task.task.theme.name,
                'task': solving__.student_task.task.name,
                'status': solving__.student_task.student_task_status.name,
                'id': solving__.id
            })
        return render_template('solving.html', tasks=tasks_)
    else:
        return redirect('/')


@app.route('/review/<int:id_>', endpoint='review_id')
@login_is_required
def review_id(id_):
    review__ = db.session.query(Review).where(Review.id == id_).first()
    data = {
        'message': review__.message,
        'requirement': [],
    }
    for review_comment__ in db.session.query(ReviewComment).where(ReviewComment.review_id == review__.id).all():
        data['requirement'].append({
            'text': review_comment__.requirement.text,
            'message': review_comment__.message,
        })
    return render_template('review_id.html', review=data)


@app.route('/student_task/<int:id_>', endpoint='student_task_id', methods=['POST', 'GET'])
@login_is_required
def student_task_id(id_):
    student_task__ = StudentTask.query.filter_by(id=id_).first()
    if request.method == 'POST':
        if 'zip' in request.files:
            zip_file = request.files['zip']
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
        'link': student_task__.task.link,
        'count_review': student_task__.task.review_count,
        'load_file': student_task__.student_task_status_id != 5,
        'requirement': [],
        'solving': [],
    }

    for requirement__ in Requirement.query.filter_by(task_id=student_task__.task_id).all():
        student_task_['requirement'].append(requirement__.text)

    for solving_ in Solving.query.filter_by(student_task_id=student_task__.id).all():
        student_task_['solving'].append({
            'file_name': solving_.file_name,
            'file_path': solving_.file_path,
            'review_count': solving_.review_count,
            'created_at': solving_.created_at,
        })
        review__ = Review.query.where((Review.solving_id == solving_.id) & (Review.review_status_id == 2)).first()
        review_ = {}
        if review__:
            review_ = {
                'status': review__.review_status.name,
                'id': review__.id,
            }
        student_task_['solving'][-1]['review'] = review_

    return render_template('student_task_id.html', student_task=student_task_)


@app.route('/student_task', endpoint='student_task')
@login_is_required
def student_task():
    student_task_ = []
    query__ = db.session.query(StudentTask)
    query__ = query__.where(StudentTask.student_id == session['user_id'])
    query__ = query__.order_by(StudentTask.student_task_status_id)
    for student_task__ in query__.all():
        student_task_.append({
            'discipline': student_task__.task.theme.discipline.name,
            'theme': student_task__.task.theme.name,
            'task': student_task__.task.name,
            'status': student_task__.student_task_status.name,
            'id': student_task__.id
        })
    return render_template('student_task.html', student_task=student_task_)


@app.route('/student_discipline', endpoint='student_discipline', methods=['POST'])
@login_is_required
def student_discipline():
    if 'student' in request.form:
        print(request.form)
        student_discipline__ = StudentDiscipline(student_id=request.form['student'],
                                                 discipline_id=request.form['discipline'])
        db.session.add(student_discipline__)
        task__ = db.session.query(Task)
        task__ = task__.join(Theme, Theme.id == Task.theme_id)
        task__ = task__.filter(Theme.discipline_id == request.form['discipline'])
        for task__ in task__.all():
            db.session.add(
                StudentTask(student_id=student_discipline__.student_id, task_id=task__.id))
        db.session.commit()
    return redirect(url_for('theme', discipline=request.form['discipline'], not_discipline=''))


@app.route('/sign-in', endpoint='sign-in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    session['user_id'] = user.id
                    session['first_name'] = user.first_name
                    session['user_type'] = []
                    if Student.query.filter_by(user_id=user.id).all():
                        session['user_type'].append('student')
                    if Teacher.query.filter_by(user_id=user.id).all():
                        session['user_type'].append('teacher')
                    return redirect('/solving')
                else:
                    return redirect('sign-in?mess=Пароль не верный')
            else:
                return redirect('sign-up?mess=Нет такого пользователя')
        except Exception as ex:
            return redirect(f'sign-in?mess={str(ex)}')
    return render_template('sign-in.html')


@app.route('/sign-up', endpoint='sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    return sign_in()
                return redirect('sign-up?mess=Уже зарегистрирован')
            user = User(
                email=request.form['email'],
                password_hash=hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest(),
                last_name=request.form['last_name'],
                first_name=request.form['first_name'],
                middle_name=request.form['middle_name']
            )
            db.session.add(user)
            db.session.commit()
            student = Student(
                user_id=user.id,
                group_id=1,
                student_status_id=1,
            )
            db.session.add(student)
            db.session.commit()
            return sign_in()
        except Exception as ex:
            return redirect(f'sign-up?mess={str(ex)}')
    return render_template('sign-up.html')


@app.route('/api/<request_>', endpoint='api')
@login_is_required
def api(request_):
    switch = {
        'student': api_student,
    }
    if request_ in switch:
        return jsonify(switch[request_]())
    else:
        return jsonify(error='Нельзя сотворить здесь')


def api_group():
    result = []
    for group__ in Group.query.all():
        result.append({
            'id': group__.id,
            'name': group__.name,
        })
    return result


def api_student():
    student_ = []
    if request.method == 'GET':
        student__ = db.session.query(Student)
        if 'not_discipline' in request.args:
            student__ = student__.join(StudentDiscipline, Student.user_id == StudentDiscipline.student_id, isouter=True)
            student__ = student__.filter(StudentDiscipline.student_id.is_(None))
        if 'group' in request.args:
            student__ = student__.filter(Student.group_id == request.args['group'])
        for student__ in student__.all():
            student_.append({
                'user_id': student__.user_id,
                'first_name': student__.user.first_name,
                'last_name': student__.user.last_name,
                'middle_name': student__.user.middle_name,
                'group_id': student__.group_id
            })
        return student_
    return student_


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


class StudentDiscipline(db.Model):
    __tablename__ = 'StudentDiscipline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    discipline_id = db.Column(db.Integer, db.ForeignKey('Discipline.id'), nullable=False)
    discipline = db.relationship('Discipline')

    student_id = db.Column(db.Integer, db.ForeignKey('Student.user_id'), nullable=False)
    student = db.relationship('Student')

    __table_args__ = (
        db.UniqueConstraint('discipline_id', 'student_id'),
    )

    def __repr__(self):
        return f'<StudentDiscipline {self.student_id} {self.discipline_id}>'


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    message = db.Column(db.String(256))

    teacher_id = db.Column(db.Integer, db.ForeignKey('Teacher.user_id'))
    teacher = db.relationship("Teacher")

    student_id = db.Column(db.Integer, db.ForeignKey('Student.user_id'))
    student = db.relationship("Student")

    review_status_id = db.Column(db.Integer, db.ForeignKey('ReviewStatus.id'), default=1, nullable=False)
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
    link = db.Column(db.String(2048), nullable=False)

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
