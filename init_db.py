#!/usr/bin/python
# coding=utf-8

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from app.models import *
import hashlib

teacher_user = User(
    email='teacher@test.ru',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    last_name='Силенок',
    first_name='Преподаватель',
    middle_name='Викторович'
).save()

group1 = Group(name='11-ИСбо-2а')
group2 = Group(name='11-ИСбо-2б')
group1.save()
group2.save()

student_status1 = StudentStatus(name='Обучается')
student_status2 = StudentStatus(name='Отчислен')
student_status1.save()
student_status2.save()

for i in range(6):
    user = User(
        email=f'student{i}@test.ru',
        password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
        last_name=f'Силенок{i}',
        first_name=f'Студент{i}',
        middle_name='Викторович'
    ).save()
    student = Student(user=user, group=group1 if i % 2 == 0 else group2, student_status=student_status1)
    student.save()

departament = Departament(name='Кафедра информационных систем и технологий')
departament.save()
teacher = Teacher(user=teacher_user, departament=departament).save()

discipline = Discipline(name='Технологии разработки программного обеспечения', author=teacher, departament=departament)
discipline.save()

theme = Theme(name='Основные команды git', discipline=discipline)
theme.save()
task = Task(name='Команды git: status, add, commit, pull, push',
            link='https://docs.google.com/document/d/12eNIkKQMNFFMKclngzeCvHl3nISay9R6UvPJLdhQeQQ/edit?usp=sharing',
            theme=theme, review_count=5)
task.save()

Requirement(text='Первый коммит содержит игнорирование файлов с расширением zip', task=task).save()
Requirement(text='Второй коммит содержит игнорирование файлов с расширением zip', task=task).save()

StudentTaskStatus(name='Не начата').save()
StudentTaskStatus(name='Требует исправлений').save()
StudentTaskStatus(name='Ожидает проверки студентом').save()
StudentTaskStatus(name='Ожидает проверки преподавателем').save()
StudentTaskStatus(name='Зачтено').save()

ReviewStatus(name='Одобрено').save()
ReviewStatus(name='Переделать').save()
