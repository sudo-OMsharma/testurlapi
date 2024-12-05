from django.urls import path
from . import views

urlpatterns = [
    path('start', views.process_url, name='testurl'),
]
