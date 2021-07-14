from app import *

user_id = 2

my_st__ = db.session.query(StudentTask).where(
    (StudentTask.student_id == user_id) & (StudentTask.student_task_status_id != 5)).subquery('t')
st__ = db.session.query(StudentTask, Solving, func.max(Solving.id))
st__ = st__.join(Solving, Solving.student_task_id == StudentTask.id)
st__ = st__.join(Review, Review.solving_id == Solving.id, isouter=True)
st__ = st__.join(my_st__, my_st__.c.task_id == StudentTask.task_id)
st__ = st__.where((StudentTask.student_task_status_id == 3) & (StudentTask.student_id != user_id))
st__ = st__.group_by(StudentTask.id)

for i__ in db.session.query(StudentTask).where(StudentTask.student_id == user_id).all():
    print(i__)

result = []
for st__ in st__.all():
    not_my = False
    for r__ in db.session.query(Review).where(st__[1].id == Review.solving_id).all():
        if r__.student.user.id == user_id:
            mot_my = True
            break
    if not not_my:
        result.append(st__[1])

print(result)

query = db.session.query(StudentTask, Solving, Review)
query = query.join(Review, Review.solving_id == Solving.id, isouter=True)
query = query.join(StudentTask, StudentTask.id == Solving.student_task_id)

for student_task in db.session.query(StudentTask).all():
    print(student_task.id, student_task.student.user.id, student_task.task.name, student_task.student.user.first_name,
          student_task.student_task_status.name)
    for solving in db.session.query(Solving).where(Solving.student_task_id == student_task.id).all():
        print('\t', solving.id, solving.created_at)
        for review in db.session.query(Review).where(Review.solving_id == solving.id).all():
            print('\t', '\t', review.id, review.created_at,
                  review.student.user.id if review.student else review.teacher.user.id,
                  review.student.user.first_name if review.student else review.teacher.user.first_name,
                  review.review_status.name)
