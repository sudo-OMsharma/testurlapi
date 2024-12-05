from django.urls import path
from . import views

urlpatterns = [
    path('start', views.del_file, name='del_file'),
]
