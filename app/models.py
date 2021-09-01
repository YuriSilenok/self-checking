from datetime import datetime

from django.db import models


class User(models.Model):
    __tablename__ = 'User'

    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=datetime.utcnow)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Group(models.Model):
    __tablename__ = 'Group'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'


class StudentStatus(models.Model):
    __tablename__ = 'StudentStatus'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Статус студента'
        verbose_name_plural = 'Статусы студента'


class Student(models.Model):
    __tablename__ = 'Student'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student_status = models.ForeignKey(StudentStatus, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class StudentTaskStatus(models.Model):
    __tablename__ = 'StudentTaskStatus'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Статус задачи студента'
        verbose_name_plural = 'Статусы задачи студента'


class Departament(models.Model):
    __tablename__ = 'Departament'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'


class Teacher(models.Model):
    __tablename__ = 'Teacher'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    departament = models.ForeignKey(Departament, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'


class Discipline(models.Model):
    __tablename__ = 'Discipline'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    author = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    departament = models.ForeignKey(Departament, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'


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


class StudentTask(models.Model):
    __tablename__ = 'StudentTask'

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.utcnow)
    score = models.IntegerField(default=1)

    student_task_status = models.ForeignKey(StudentTaskStatus, on_delete=models.CASCADE)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student} {self.task}'

    class Meta:
        verbose_name = 'Задача студента'
        verbose_name_plural = 'Задачи студентов'


class StudentDiscipline(models.Model):
    __tablename__ = 'StudentDiscipline'

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.utcnow)

    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('discipline_id', 'student_id'),)
        verbose_name = 'Изучаемая дисциплина студентом'
        verbose_name_plural = 'Изучаемые дисциплины студентами'

    def __str__(self):
        return f'{self.discipline} {self.student}'


class ReviewStatus(models.Model):
    __tablename__ = 'ReviewStatus'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Статус проверки'
        verbose_name_plural = 'Статусы проверок'


class Solving(models.Model):
    __tablename__ = 'Solving'

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.utcnow)
    file_name = models.CharField(max_length=256)
    file_path = models.CharField(max_length=256)
    review_count = models.IntegerField()

    student_task = models.ForeignKey(StudentTask, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.student_task} {self.created_at} {self.review_count}'

    class Meta:
        verbose_name = 'Решение'
        verbose_name_plural = 'Решения'


class Review(models.Model):
    __tablename__ = 'Review'

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.utcnow)
    message = models.CharField(max_length=256)

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    review_status = models.ForeignKey(ReviewStatus, on_delete=models.CASCADE, default=1)

    solving = models.ForeignKey(Solving, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.solving} {self.review_status} {self.created_at} {self.message}'

    class Meta:
        verbose_name = 'Проверка'
        verbose_name_plural = 'Проверки'


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


class ReviewComment(models.Model):
    __tablename__ = 'ReviewComment'

    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=256)

    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.review} {self.requirement} {self.message}'

    class Meta:
        verbose_name = 'Комментарий к проверке'
        verbose_name_plural = 'Комментарии к проверке'
