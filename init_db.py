from main import *
import hashlib

db.drop_all()
db.create_all()
db.session.commit()

db.session.add(User(
    email='zena@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    surname='Силенок',
    name='Юрий',
    middle_name='Викторович'
))
db.session.add(TaskStatus(name='Не начата'))
db.session.add(TaskStatus(name='Выполняется'))
db.session.add(TaskStatus(name='Завершена'))
db.session.add(Discipline(name='ТРПО'))
db.session.commit()

db.session.add(Theme(
    name='Как писать письма?',
    discipline_id=Discipline.query.filter_by(name='ТРПО').first().id,
))
db.session.commit()

db.session.add(Task(
    name="ЛР01",
    review_count=5,
    text="Что-то нужно сделать",
    theme_id=Discipline.query.filter_by(name='ТРПО').first().id,
))
db.session.add(Task(
    name="ЛР02",
    review_count=5,
    text="Что-то нужно сделать2",
    theme_id=Discipline.query.filter_by(name='ТРПО').first().id,
))
db.session.commit()

db.session.add(UserTask(
    user_id=User.query.filter_by(email='zena@zizni.net').first().id,
    task_id=Task.query.filter_by(name='ЛР01').first().id,
    status_id=TaskStatus.query.filter_by(name='Не начата').first().id,
))
db.session.add(UserTask(
    user_id=User.query.filter_by(email='zena@zizni.net').first().id,
    task_id=Task.query.filter_by(name='ЛР02').first().id,
    status_id=TaskStatus.query.filter_by(name='Не начата').first().id,
))
db.session.commit()

db.session.add(TaskRequirement(
    text='Требование 1',
    task_id=Task.query.filter_by(name='ЛР01').first().id,
))
db.session.commit()
