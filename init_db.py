from main import *
import hashlib

db.drop_all()
db.create_all()
db.session.commit()

db.session.add(User(
    email='zena1@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    last_name='Силенок',
    first_name='Преподаватель',
    middle_name='Викторович'
))
db.session.add(User(
    email='zena2@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    last_name='Силенок',
    first_name='Студент1',
    middle_name='Викторович'
))
db.session.add(User(
    email='zena3@zizni.net',
    password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
    last_name='Силенок',
    first_name='Студент2',
    middle_name='Викторович'
))
db.session.add(Departament(name='Кафедра информационных систем и технологий'))
db.session.add(Teacher(user_id=1, departament_id=1))
db.session.add(StudentStatus(name='Обучается'))
db.session.add(StudentStatus(name='Отчислен'))
db.session.add(Group(name='11-ИСбо-2а'))
db.session.add(Student(user_id=2, group_id=1, student_status_id=1))
db.session.add(Student(user_id=3, group_id=1, student_status_id=1))
db.session.add(Discipline(name='Технологии разработки программного', author_id=1, departament_id=1))
db.session.add(Theme(name='Основные команды git', discipline_id=1))
db.session.add(
    Task(name='Команды git: status, add, commit, pull, push', text='Просто сделайте это', theme_id=1, review_count=5))
db.session.add(Requirement(text='Первый коммит содержит игнорирование файлой с расширением zip', task_id=1))
db.session.add(StudentTaskStatus(name='Не начата'))
db.session.add(StudentTaskStatus(name='Требует исправлений'))
db.session.add(StudentTaskStatus(name='Ожидает проверки студентом'))
db.session.add(StudentTaskStatus(name='Ожидает проверки преподавателем'))
db.session.add(StudentTaskStatus(name='Зачтено'))
db.session.add(StudentTask(student_id=2, task_id=1))
db.session.add(ReviewStatus(name='Одобрено'))
db.session.add(ReviewStatus(name='Переделать'))

db.session.commit()
