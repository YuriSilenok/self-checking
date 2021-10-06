import hashlib
import os

from app.models import *
from django.shortcuts import render, redirect
from django import template
from django.db.models import F

register = template.Library()
UPLOAD_FOLDER = 'files'


def sign_in(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
            if user:
                if user.password_hash == hashlib.sha1(request.POST['password'].encode('utf-8')).hexdigest():
                    request.session['user_id'] = user.id
                    request.session['first_name'] = user.first_name
                    request.session['last_name'] = user.last_name
                    request.session['user_type'] = []
                    if Student.objects.filter(user_id=user.id).first():
                        request.session['user_type'].append('student')
                    if Teacher.objects.filter(user_id=user.id).first():
                        request.session['user_type'].append('teacher')
                    return redirect('/')
                return redirect('/sign-in?mess=Пароль не верный')
            return redirect('/sign-up?mess=Нет такого пользователя')
        except Exception as ex:
            return redirect(f'/sign-in?mess={str(ex)}')
    return render(request, 'sign-in.html')


def sign_up(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST['email'])
            if user:
                if user.password_hash == hashlib.sha1(request.POST['password'].encode('utf-8')).hexdigest():
                    return redirect('/sign-in')
                return redirect('/sign-up?mess=Уже зарегистрирован')
            user = User(
                email=request.POST['email'],
                password_hash=hashlib.sha1(request.POST['password'].encode('utf-8')).hexdigest(),
                last_name=request.POST['last_name'],
                first_name=request.POST['first_name'],
                middle_name=request.POST['middle_name']
            )
            user.save()

            student = Student(
                user_id=user.id,
                group_id=1,
                student_status_id=1,
            )
            student.save()
            return redirect('/sign-in')
        except Exception as ex:
            return redirect(f'sign-up?mess={str(ex)}')
    return render(request, 'sign-up.html')


def logout(request):
    if 'user_id' in request.session:
        request.session.pop('user_id')
    if 'first_name' in request.session:
        request.session.pop('first_name')
    if 'last_name' in request.session:
        request.session.pop('last_name')
    if 'user_type' in request.session:
        request.session.pop('user_type')
    return redirect('/sign-in')


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user_id" in args[0].session:
            return function(*args, **kwargs)
        return redirect('/sign-in')

    return wrapper


@register.inclusion_tag('header.html')
def user_type(request):
    return request.session.get('user_type', [])


@register.inclusion_tag('header.html')
def first_name(request):
    return f" {request.session.get('first_name', 'Гость')}  {request.session.get('last_name', '')}"


@login_is_required
def solving(request):
    data = []
    if 'student' in request.session['user_type']:
        data = StudentTask.objects.exclude(student_id=request.session['user_id']).filter(student_task_status_id=3)
    if 'teacher' in request.session['user_type']:
        data = StudentTask.objects.filter(student_task_status__id=4).filter(
            task__theme__discipline__author__user__id=request.session['user_id'])
    return render(request, 'solving.html', {'data': data})


def index(request):
    return redirect('/solving')


@login_is_required
def solving_id(request, id_):
    return render(request, 'solving_id.html')


@login_is_required
def discipline(request):
    if request.method == 'POST':
        user_ = User.objects.get(id=request.session['user_id'])
        teacher_ = Teacher.objects.get(user=user_)
        Discipline(name=request.POST['name'], author=teacher_).save()
    return render(request, 'discipline.html', {'data': Discipline.objects.filter(author=request.session['user_id'])})


@login_is_required
def discipline_id(request, id_):
    discipline_ = Discipline.objects.get(id=id_)
    if request.method == 'POST':
        Theme(discipline=discipline_, name=request.POST['name']).save()
    return render(request, 'discipline_id.html', {
        'data': Theme.objects.filter(discipline=id_),
        'discipline': discipline_,
        'groups': Group.objects.all(),
        'students': Student.objects.filter(student_status=1).exclude(studentdiscipline__student=F('user'))})


@login_is_required
def student_discipline(request, id_):
    if request.method == 'POST' and 'student' in request.POST:
        student_ = Student.objects.get(user=request.POST['student'])
        StudentDiscipline(student=student_,
                          discipline=Discipline.objects.get(id=id_)).save()
        for theme in Theme.objects.filter(discipline=id_):
            for task in Task.objects.filter(theme=theme):
                StudentTask(student=student_, task=task).save()
    return redirect(f'/discipline/{id_}/')


@login_is_required
def theme_id(request, id_):
    theme_ = Theme.objects.get(id=id_)
    if request.method == 'POST':
        Task(
            theme=theme_,
            name=request.POST['name'],
            link=request.POST['link'],
            review_count=request.POST['review_count'],
        ).save()
    data = []
    for row in Task.objects.filter(theme=id_):
        data.append({
            'id': row.id,
            'name': row.name,
        })
    return render(request, 'theme_id.html', {'data': data})


@login_is_required
def task_id(request, id_):
    task_ = Task.objects.get(id=id_)
    if request.method == 'POST':
        Requirement(task=task_, text=request.POST['text']).save()
    data = []
    for row in Requirement.objects.filter(task=id_):
        data.append({
            'id': row.id,
            'text': row.text,
        })
    return render(request, 'task_id.html', {'data': data})


@login_is_required
def student_task(request):
    return render(request, 'student_task.html',
                  {'data': StudentTask.objects.filter(student_id=request.session['user_id'])})


@login_is_required
def student_task_id(request, id_):
    student_task_ = StudentTask.objects.get(id=id_)
    if request.method == 'POST' and 'zip' in request.FILES:
        zip_file = request.FILES['zip']
        if zip_file.filename != '':
            solving_ = Solving(
                file_path='file_path',
                file_name='file_name',
                review_count=0,
                student_task=student_task_,
            )
            solving_.save()
            file_path = os.path.join('task', str(solving_.student_task.task.id), 'solving', str(solving_.id))
            full_file_path = os.path.join(UPLOAD_FOLDER, file_path)
            solving_.file_path = file_path
            solving_.file_name = zip_file.filename
            student_task_.student_task_status_id = 3
            solving_.save()
            if not os.path.exists(full_file_path):
                os.makedirs(full_file_path)
            zip_file.save(os.path.join(full_file_path, zip_file.filename))

    return render(request, 'student_task_id.html',
                  {'student_task': student_task_,
                   'requirements': Requirement.objects.filter(task=student_task_.task),
                   'load_file': student_task_.student_task_status.id != 5,
                   'solving': Solving.objects.filter(student_task=student_task_)
                   })



