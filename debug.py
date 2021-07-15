from app import *

query__ = db.session.query(Review, ReviewComment) \
    .join(Review, Review.id == ReviewComment.review_id, isouter=True) \
    .where(Review.id == 12)

for q_ in query__.all():
    print(q_)

query = db.session.query(StudentTask, Solving, Review)
query = query.join(Review, Review.solving_id == Solving.id, isouter=True)
query = query.join(StudentTask, StudentTask.id == Solving.student_task_id)

for student_task in db.session.query(StudentTask).all():
    print(student_task.id, student_task.task.name, student_task.student.user.first_name,
          student_task.student_task_status.name)
    for solving in db.session.query(Solving).where(Solving.student_task_id == student_task.id).all():
        print('\t', solving.id, solving.created_at)
        for review in db.session.query(Review).where(Review.solving_id == solving.id).all():
            print('\t', '\t', review.id, review.created_at,
                  review.student.user.id if review.student else review.teacher.user.id,
                  review.student.user.first_name if review.student else review.teacher.user.first_name,
                  review.review_status.name,
                  review.message)
