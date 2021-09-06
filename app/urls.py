from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('favicon', views.favicon, name='favicon'),
    path('', views.sign_in, name='sign_in'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout, name='logout'),
    path('solving', views.solving, name='solving'),
]
