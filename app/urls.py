from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout, name='logout'),
    path('solving', views.solving, name='solving'),
    path('solving/<int:id_>/', views.solving_id, name='solving_id'),
    path('student_task', views.student_task, name='student_task'),
    path('student_task/<int:id_>/', views.student_task_id, name='student_task_id'),
    path('discipline', views.discipline, name='discipline'),
    path('discipline/<int:id_>/', views.discipline_id, name='discipline_id'),
    path('theme/<int:id_>/', views.theme_id, name='theme_id'),
    path('task/<int:id_>/', views.task_id, name='task_id'),
    path('discipline/<int:id_>/student_discipline', views.student_discipline, name='student_discipline'),
    path('review_id/<int:id_>/', views.student_task_id, name='review_id'),
]
