from django.contrib import admin
from .models import *
from django.contrib.auth.models import User


# class TeacherInline(admin.StackedInline):
#     model = Teacher
#     can_delete = False
#     verbose_name_plural = 'teacher'
#
#
# class TeacherUser(User):
#     inlines = (TeacherInline,)


# admin.site.unregister(User)
# admin.site.register(User, Teacher)
admin.site.register(Teacher)
admin.site.register(Student)

admin.site.register(Group)
admin.site.register(StudentStatus)
admin.site.register(StudentTaskStatus)
admin.site.register(Departament)
admin.site.register(Discipline)
admin.site.register(Theme)
admin.site.register(Task)
admin.site.register(StudentTask)
admin.site.register(StudentDiscipline)
admin.site.register(ReviewStatus)
admin.site.register(Solving)
admin.site.register(Review)
admin.site.register(Requirement)
admin.site.register(ReviewComment)
