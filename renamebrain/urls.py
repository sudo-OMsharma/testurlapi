from django.urls import path
from . import views

urlpatterns = [
    path('start', views.renamebrain, name='renamebrain'),
]
