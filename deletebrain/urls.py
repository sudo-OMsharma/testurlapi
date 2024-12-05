from django.urls import path
from . import views

urlpatterns = [
    path('start', views.deletebrain, name='deletebrain'),
]
