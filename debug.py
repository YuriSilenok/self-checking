from app import *

# query = db.session.query(StudentTask, Solving, Review)
# query = query.join(Review, Review.solving_id == Solving.id, isouter=True)
# query = query.join(StudentTask, StudentTask.id == Solving.student_task_id)
# query = query.where((StudentTask.student_task_status_id == 3) & (Solving.review_status_id == 1) & (Review.student_id != 3))

for student_task in db.session.query(StudentTask).all():
    print(student_task.id, student_task.task.name, student_task.student.user.first_name,
          student_task.student_task_status.name)
    for solving in db.session.query(Solving).where(Solving.student_task_id == student_task.id).all():
        print('\t', solving.id, solving.created_at)
        for review in db.session.query(Review).where(Review.solving_id == solving.id).all():
            print('\t', '\t', review.id, review.created_at,
                  review.student.user.id if review.student else review.teacher.user.id,
                  review.student.user.first_name if review.student else review.teacher.user.first_name,
                  review.review_status.name)


query__ = db.session.query(Solving)
query__ = query__.join(StudentTask, Solving.student_task_id == StudentTask.id)
query__ = query__.join(Review, Review.solving_id == Solving.id, isouter=True)
query__ = query__.where(StudentTask.student_task_status_id == 3)
query__ = query__.group_by(Solving.student_task_id)


exists__ = db.session.query(Solving, Solving.id)
exists__ = exists__.join(StudentTask, Solving.student_task_id == StudentTask.id)
exists__ = exists__.join(Review, Review.solving_id == Solving.id, isouter=True)
exists__ = exists__.group_by(Solving.student_task_id)
exists__ = exists__.having(Review.student_id == 7)


print('===')
print(query__)
print('===')
for s in query__.all():
    print(s)
print('===')
print(exists__)
print('===')
for s in exists__.all():
    print(s)
print('===')

# SA = query__.subquery('SA')
# SB = exists__.subquery('SB')

# finish__ = db.session.query(SA).join(SB, SB.c.id == SA.c.id, isouter=True).where(SB.c.id.is_(None))
finish__ = query__.filter(~exists__.exists())
print(finish__)
print('===')
for s in finish__.all():
    print(s)
print('===')
