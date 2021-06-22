from main import *
import hashlib

db.drop_all()
db.create_all()
db.session.commit()
user1 = User(
    email='zena@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    surname='Силенок',
    name='Юрий',
    middle_name='Викторович'
)
user2 = User(
    email='zena2@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    surname='Силенок',
    name='Юрий',
    middle_name='Викторович'
)
db.session.add(user1)
db.session.add(user2)
departament = Departament(name='Кафедра информационных систем и технологий')
db.session.add(departament)
db.session.commit()
user1 = User.query.filter_by(email=user1.email).first()
user2 = User.query.filter_by(email=user2.email).first()
departament = Departament.query.filter_by(name=departament.name).first()
teacher = Teacher(user_id=user1.id, departament_id=departament.id)
db.session.add(teacher)
db.session.add(StudentStatus(name='Обучается'))
db.session.add(StudentStatus(name='Отчислен'))
db.session.add(Group(name='11-ИСбо-2а'))
db.session.commit()
student_status = StudentStatus.query.filter_by(name='Обучается').first()
group = Group.query.filter_by(name='11-ИСбо-2а').first()
student = Student(user_id=user2.id,group_id=group.id, student_status_id=student_status.id)
db.session.add(student)
db.session.add(Discipline(name='Технологии разработки программного'))




db.session.add(Theme(
    name='Как писать письма?',
    discipline_id=Discipline.query.filter_by(name='ТРПО').first().id,
))
db.session.commit()



db.session.add(Task(
    name="ЛР01",
    review_count=5,
    text="Составить письмо, где Вы обращаетесь к HR с выражением желания пройти практику в компании",
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
    text='Тело письма должна иметь приветсвие',
    task_id=Task.query.filter_by(name='ЛР01').first().id,
))
db.session.add(TaskRequirement(
    text='После приветствия должна быть пустая строка',
    task_id=Task.query.filter_by(name='ЛР01').first().id,
))
db.session.commit()
