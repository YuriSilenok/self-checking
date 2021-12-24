from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class StudentGroup(models.Model):
    __tablename__ = 'StudentGroup'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'


class UserStudentGroup(models.Model):
    __tablename__ = 'UserStudentGroup'

    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)


class Discipline(models.Model):
    __tablename__ = 'Discipline'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


class StudentGroupDiscipline(models.Model):
    __tablename__ = 'StudentGroupDiscipline'

    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        unique_together = (('discipline', 'student_group'),)
        verbose_name = 'Изучаемая дисциплина группой'
        verbose_name_plural = 'Изучаемые дисциплины группами'

    def __str__(self):
        return f'{self.discipline} {self.student_group}'


class Theme(models.Model):
    __tablename__ = 'Theme'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'


class Task(models.Model):
    __tablename__ = 'Task'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    review_count = models.IntegerField()
    link = models.CharField(max_length=2048)

    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class Requirement(models.Model):
    __tablename__ = 'Requirement'

    id = models.AutoField(primary_key=True)
    text = models.TextField()

    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.text)

    class Meta:
        verbose_name = 'Требование'
        verbose_name_plural = 'Требования'


class StudentTaskStatus(models.Model):
    __tablename__ = 'StudentTaskStatus'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Статус задачи студента'
        verbose_name_plural = 'Статусы задачи студента'


class StudentTask(models.Model):
    __tablename__ = 'StudentTask'

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.utcnow)
    score = models.IntegerField(default=0)
    student_task_status = models.ForeignKey(StudentTaskStatus, default=1, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student} {self.task}'

    class Meta:
        verbose_name = 'Задача студента'
        verbose_name_plural = 'Задачи студентов'


class Solving(models.Model):
    __tablename__ = 'Solving'

    id = models.AutoField(primary_key=True)
    student_task = models.ForeignKey(StudentTask, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=256)
    file_path = models.CharField(max_length=256)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f'{self.student_task} {self.created_at} {self.review_count}'

    class Meta:
        verbose_name = 'Решение'
        verbose_name_plural = 'Решения'


class ReviewStatus(models.Model):
    __tablename__ = 'ReviewStatus'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Статус проверки'
        verbose_name_plural = 'Статусы проверок'


class Review(models.Model):
    __tablename__ = 'Review'

    id = models.AutoField(primary_key=True)
    solving = models.ForeignKey(Solving, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.utcnow)
    message = models.CharField(max_length=256)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    review_status = models.ForeignKey(ReviewStatus, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.solving} {self.review_status} {self.created_at} {self.message}'

    class Meta:
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'


class ReviewComment(models.Model):
    __tablename__ = 'ReviewComment'

    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    message = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.review} {self.requirement} {self.message}'

    class Meta:
        verbose_name = 'Комментарий к проверке'
        verbose_name_plural = 'Комментарии к проверке'
