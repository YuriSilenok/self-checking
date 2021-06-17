from main import *
import hashlib

db.create_all()
db.session.add(
    User(
        email='zena@zizni.net',
        password_hash=hashlib.sha1(r'123').hexdigest(),
        surname='Силенок',
        name='Юрий',
        middle_name='Викторович'
    )
)
db.session.add(
    DisciplineStatus(
        email='zena@zizni.net',
        password_hash=hashlib.sha1(r'123').hexdigest(),
        surname='Силенок',
        name='Юрий',
        middle_name='Викторович'
    )
)
