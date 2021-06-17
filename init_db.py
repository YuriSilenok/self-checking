from main import *
import hashlib

db.drop_all()
db.create_all()
db.session.commit()
user = User(
        email='zena@zizni.net',
        password_hash=hashlib.sha1('123'.encode('utf-8')).hexdigest(),
        surname='Силенок',
        name='Юрий',
        middle_name='Викторович'
    )
db.session.add(user)
todo = DisciplineStatus(name='Не начата')
db.session.add(todo)
db.session.add(DisciplineStatus(name='Выполняется'))
db.session.add(DisciplineStatus(name='Завершена'))
trpo = Discipline(name='ТРПО')
db.session.add(trpo)
trpo = Discipline.query.filter_by(name='ТРПО').first()
theme1 = Theme(name='Как писать письма?', discipline_id=trpo.id)
db.session.commit()
db.session.add(theme1)
db.session.commit()
