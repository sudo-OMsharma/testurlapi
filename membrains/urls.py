from django.urls import path
from . import views

urlpatterns = [
    path('start', views.membrains, name='membrains'),
]
