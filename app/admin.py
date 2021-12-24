from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

admin.site.register(UserStudentGroup)
admin.site.register(StudentGroup)
admin.site.register(StudentGroupDiscipline)
admin.site.register(Discipline)
admin.site.register(Theme)
admin.site.register(Task)
admin.site.register(Requirement)
admin.site.register(StudentTask)
admin.site.register(StudentTaskStatus)
admin.site.register(Solving)
admin.site.register(Review)
admin.site.register(ReviewStatus)
admin.site.register(ReviewComment)
