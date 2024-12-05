from django.urls import path
from . import views

urlpatterns = [
    path('start', views.del_embedding_from_runtime, name='deleteram'),
]
