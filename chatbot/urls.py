from django.urls import path
from . import views

urlpatterns = [
    path('start',views.chatbot, name='chatbot')
]
