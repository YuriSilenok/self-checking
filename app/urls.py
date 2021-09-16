from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout, name='logout'),
    path('solving', views.solving, name='solving'),
    path('solving/<int:id_>', views.solving_id, name='solving_id'),
    path('student_task', views.solving, name='student_task'),
    path('discipline', views.solving, name='discipline'),

]
