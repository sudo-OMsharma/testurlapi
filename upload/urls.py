from django.urls import path
from . import views

urlpatterns = [
    path('start', views.upload_file, name='upload'),
]
