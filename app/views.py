import hashlib
import os

from django.http import HttpResponse
from flask import send_from_directory

from app.models import *
from django.shortcuts import render, redirect

UPLOAD_FOLDER = 'files'


def sign_in(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.form['email'])
            if user:
                if user.password_hash == hashlib.sha1(request.form['password'].encode('utf-8')).hexdigest():
                    request.session['user_id'] = user.id
                    request.session['first_name'] = user.first_name
                    request.session['last_name'] = user.last_name
                    request.session['user_type'] = []
                    if Student.objects.filter(user_id=user.id):
                        request.session['user_type'].append('student')
                    if Teacher.objects.filter(user_id=user.id):
                        request.session['user_type'].append('teacher')
                    return redirect('/solving')
                else:
                    return redirect('sign-in?mess=Пароль не верный')
            else:
                return redirect('sign-up?mess=Нет такого пользователя')
        except Exception as ex:
            return redirect(f'sign-in?mess={str(ex)}')
    return render(request, 'sign-in.html', content_type='application/xhtml+xml')


def sign_up(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.form['email'])
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
    return render(request, 'sign-up.html')


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" in args[0].session:
            return function(*args, **kwargs)
        else:
            return redirect('sign-in')

    return wrapper


def favicon(request):
    return HttpResponse(open(os.path.join(os.getcwd(), 'static', 'favicon.ico'), "rb").read())
# @login_is_required
# def solving(request):
#     if 'student' in request.session['user_type']:
#         tasks_ = []
#         my_st__ = db.session.objects(StudentTask) \
#             .where((StudentTask.student_id == request.session['user_id']) & (StudentTask.student_task_status_id != 5)) \
#             .subquery('t')
#         st__ = db.session.objects(StudentTask, Solving, func.max(Solving.id)) \
#             .join(Solving, Solving.student_task_id == StudentTask.id) \
#             .join(Review, Review.solving_id == Solving.id, isouter=True) \
#             .join(my_st__, my_st__.c.task_id == StudentTask.task_id) \
#             .where((StudentTask.student_task_status_id == 3) & (StudentTask.student_id != request.session['user_id'])) \
#             .group_by(StudentTask.id)
#
#         for st__ in st__:
#             not_my = True
#             for r__ in db.session.objects(Review).where(st__[1].id == Review.solving_id):
#                 if r__.student.user.id == request.session['user_id']:
#                     not_my = False
#                     break
#             if not_my:
#                 tasks_.append({
#                     'discipline': st__[0].task.theme.discipline.name,
#                     'theme': st__[0].task.theme.name,
#                     'task': st__[0].task.name,
#                     'status': st__[0].student_task_status.name,
#                     'id': st__[1].id,
#                 })
#         return render(request, 'solving.html', tasks=tasks_)
#     if 'teacher' in request.session['user_type']:
#         tasks_ = []
#
#         query__ = db.session.objects(Solving)
#         query__ = query__.join(StudentTask, Solving.student_task_id == StudentTask.id)
#         query__ = query__.where(StudentTask.student_task_status_id == 4)
#         query__ = query__.group_by(Solving.student_task_id)
#
#         for solving__ in query__:
#             tasks_.append({
#                 'discipline': solving__.student_task.task.theme.discipline.name,
#                 'theme': solving__.student_task.task.theme.name,
#                 'task': solving__.student_task.task.name,
#                 'status': solving__.student_task.student_task_status.name,
#                 'id': solving__.id
#             })
#         return render(request, 'solving.html', tasks=tasks_)
#     return redirect('/')
#
#
# @login_is_required
# def solving_id(request, id_):
#     solving__ = Solving.objects.get(id=id_)
#     task__ = solving__.student_task.task
#     requirement__ = Requirement.objects.filter(task_id=task__.id)
#
#     if request.method == 'POST':
#         review__ = Review(solving_id=id_)
#         if 'teacher' in request.session['user_type']:
#             review__.teacher_id = request.session['user_id']
#         if 'student' in request.session['user_type']:
#             review__.student_id = request.session['user_id']
#         review__.save()
#         for key in request.form:
#             if request.form[key]:
#                 review__.review_status_id = 2
#                 if 'requirement.' in key:
#                     requirement_id = int(key.replace('requirement.', ''))
#                     review_comment__ = ReviewComment(review_id=review__.id, requirement_id=requirement_id,
#                                                      message=request.form[key])
#                     review_comment__.save()
#             if 'common' in key:
#                 review__.message = request.form[key]
#         solving__.review_count += 1
#         if review__.review_status_id == 2:
#             solving__.student_task.student_task_status_id = 2
#         elif 'teacher' in request.session['user_type']:
#             solving__.student_task.student_task_status_id = 5
#         elif solving__.review_count >= solving__.student_task.task.review_count:
#             solving__.student_task.student_task_status_id = 4
#         return redirect('solving')
#     task_ = {
#         'name': task__.name,
#         'link': task__.link,
#         'file_path': solving__.file_path + '/' + solving__.file_name,
#         'requirement': [],
#     }
#     for requirement_ in requirement__:
#         task_['requirement'].append({
#             'id': requirement_.id,
#             'text': requirement_.text,
#         })
#     return render(request, 'solving_id.html', task=task_)

#

#
#
# @login_is_required
# def files(request, filename):
#     return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
#
#
# def global_data(request):
#     def first_name(request):
#         return f" {request.session.get('first_name', 'Гость')}  {request.session.get('last_name', '')}"
#
#     def user_type(request):
#         return request.session.get('user_type', [])
#
#     def version(request):
#         return subprocess.check_output(['git', 'describe']).decode("utf-8")
#
#     return dict(first_name=first_name, user_type=user_type, version=version)
#
#
# def logout(request):
#     if 'user_id' in request.session:
#         request.session.pop('user_id')
#     if 'first_name' in request.session:
#         request.session.pop('first_name')
#     if 'last_name' in request.session:
#         request.session.pop('last_name')
#     if 'user_type' in request.session:
#         request.session.pop('user_type')
#
#     return redirect('sign-in')
#
#
# @login_is_required
# def discipline(request):
#     if request.method == 'POST':
#         discipline__ = Discipline(
#             author_id=session['user_id'],
#             name=request.form['name'],
#             departament_id=Teacher.objects.get(user_id=session['user_id']).departament_id
#         )
#         db.session.add(discipline__)
#         db.session.commit()
#         return redirect( 'theme', discipline=discipline__.id)
#     data = []
#     for discipline__ in Discipline.objects.filter(author_id=session['user_id']):
#         data.append({
#             'id': discipline__.id,
#             'name': discipline__.name,
#         })
#     return render(request, 'discipline.html', data=data)
#
#
# @login_is_required
# def theme(request):
#     if request.method == 'POST':
#         theme__ = Theme(name=request.form['name'], discipline_id=request.args['discipline'])
#         db.session.add(theme__)
#         db.session.commit()
#         return redirect( 'task', theme=theme__.id)
#     discipline__ = Discipline.objects.get(id=request.args['discipline'])
#     if not discipline__:
#         return redirect( 'discipline')
#     themes = []
#     for theme__ in Theme.objects.filter(discipline_id=discipline__.id):
#         themes.append({
#             'id': theme__.id,
#             'name': theme__.name,
#         })
#     discipline_ = {'name': discipline__.name, 'id': discipline__.id}
#     return render(request, 'theme.html', themes=themes, discipline=discipline_, groups=api_group(),
#                   students=api_student())
#
#
# @login_is_required
# def task(request):
#     if request.method == 'POST':
#         task__ = Task(name=request.form['name'], link=request.form['link'],
#                       review_count=int(request.form['review_count']), theme_id=request.args['theme'])
#         db.session.add(task__)
#         db.session.commit()
#         return redirect( 'requirement', task=task__.id)
#     theme__ = Theme.objects.get(id=request.args['theme'])
#     if not theme__:
#         return redirect( 'theme')
#     data = []
#     for task__ in Task.objects.filter(theme_id=theme__.id):
#         data.append({
#             'id': task__.id,
#             'name': task__.name,
#             'link': task__.link,
#             'review_count': task__.review_count,
#         })
#     return render(request, 'task.html', data=data, theme=theme__.name)
#
#
# @login_is_required
# def requirement(request):
#     if request.method == 'POST':
#         requirement__ = Requirement(text=request.form['text'], task_id=request.args['task'])
#         db.session.add(requirement__)
#         db.session.commit()
#     task__ = Task.objects.get(id=request.args['task'])
#     if not task__:
#         return redirect( 'task')
#     data = []
#     for requirement__ in Requirement.objects.filter(task_id=task__.id):
#         data.append({
#             'text': requirement__.text,
#         })
#     return render(request, 'requirement.html', data=data, task=task__.name)
#
#

#
#

#
#

#
#
# @login_is_required
# def review_id(request, id_):
#     review__ = db.session.objects(Review).where(Review.id == id_).first()
#     data = {
#         'message': review__.message,
#         'requirement': [],
#     }
#     for review_comment__ in db.session.objects(ReviewComment).where(ReviewComment.review_id == review__.id):
#         data['requirement'].append({
#             'text': review_comment__.requirement.text,
#             'message': review_comment__.message,
#         })
#     return render(request, 'review_id.html', review=data)
#
#
# @login_is_required
# def student_task_id(request, id_):
#     student_task__ = StudentTask.objects.get(id=id_)
#     if request.method == 'POST':
#         if 'zip' in request.files:
#             zip_file = request.files['zip']
#             if zip_file.filename != '':
#                 solving__ = Solving(
#                     file_path='file_path',
#                     file_name='file_name',
#                     review_count=0,
#                     student_task_id=id_,
#                 )
#                 db.session.add(solving__)
#                 db.session.commit()
#                 file_path = os.path.join('task', str(solving__.student_task.task.id), 'solving', str(solving__.id))
#                 full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
#                 solving__.file_path = file_path
#                 solving__.file_name = zip_file.filename
#                 student_task__.student_task_status_id = 3
#                 db.session.commit()
#                 if not os.path.exists(full_file_path):
#                     os.makedirs(full_file_path)
#                 zip_file.save(os.path.join(full_file_path, zip_file.filename))
#
#     student_task_ = {
#         'id': student_task__.task.id,
#         'name': student_task__.task.name,
#         'link': student_task__.task.link,
#         'count_review': student_task__.task.review_count,
#         'load_file': student_task__.student_task_status_id != 5,
#         'requirement': [],
#         'solving': [],
#     }
#
#     for requirement__ in Requirement.objects.filter(task_id=student_task__.task_id):
#         student_task_['requirement'].append(requirement__.text)
#
#     for solving_ in Solving.objects.filter(student_task_id=student_task__.id):
#         student_task_['solving'].append({
#             'file_name': solving_.file_name,
#             'file_path': solving_.file_path,
#             'review_count': solving_.review_count,
#             'created_at': solving_.created_at,
#         })
#         review__ = Review.objects.where((Review.solving_id == solving_.id) & (Review.review_status_id == 2)).first()
#         review_ = {}
#         if review__:
#             review_ = {
#                 'status': review__.review_status.name,
#                 'id': review__.id,
#             }
#         student_task_['solving'][-1]['review'] = review_
#
#     return render(request, 'student_task_id.html', student_task=student_task_)
#
#
# @login_is_required
# def student_task(request):
#     student_task_ = []
#     query__ = db.session.objects(StudentTask)
#     query__ = query__.where(StudentTask.student_id == request.session['user_id'])
#     query__ = query__.order_by(StudentTask.student_task_status_id)
#     for student_task__ in query__:
#         student_task_.append({
#             'discipline': student_task__.task.theme.discipline.name,
#             'theme': student_task__.task.theme.name,
#             'task': student_task__.task.name,
#             'status': student_task__.student_task_status.name,
#             'id': student_task__.id
#         })
#     return render(request, 'student_task.html', student_task=student_task_)
#
#
# @login_is_required
# def student_discipline(request):
#     if 'student' in request.form:
#         print(request.form)
#         student_discipline__ = StudentDiscipline(student_id=request.form['student'],
#                                                  discipline_id=request.form['discipline'])
#         db.session.add(student_discipline__)
#         task__ = db.session.objects(Task)
#         task__ = task__.join(Theme, Theme.id == Task.theme_id)
#         task__ = task__.filter(Theme.discipline_id == request.form['discipline'])
#         for task__ in task__:
#             db.session.add(
#                 StudentTask(student_id=student_discipline__.student_id, task_id=task__.id))
#         db.session.commit()
#     return redirect( 'theme', discipline=request.form['discipline'], not_discipline='')
#
#

#
#
# @login_is_required
# def api(request, request_):
#     switch = {
#         'student': api_student,
#     }
#     if request_ in switch:
#         return jsonify(switch[request_]())
#     else:
#         return jsonify(error='Нельзя сотворить здесь')
#
#
# def api_group(request):
#     result = []
#     for group__ in Group.objects:
#         result.append({
#             'id': group__.id,
#             'name': group__.name,
#         })
#     return result
#
#
# def api_student(request):
#     student_ = []
#     if request.method == 'GET':
#         student__ = db.session.objects(Student)
#         if 'not_discipline' in request.args:
#             student__ = student__.join(StudentDiscipline, Student.user_id == StudentDiscipline.student_id, isouter=True)
#             student__ = student__.filter(StudentDiscipline.student_id.is_(None))
#         if 'group' in request.args:
#             student__ = student__.filter(Student.group_id == request.args['group'])
#         for student__ in student__:
#             student_.append({
#                 'user_id': student__.user_id,
#                 'first_name': student__.user.first_name,
#                 'last_name': student__.user.last_name,
#                 'middle_name': student__.user.middle_name,
#                 'group_id': student__.group_id
#             })
#         return student_
#     return student_
