"""personadjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('createbrains/', include('createbrains.urls')),
    path('deleteram/', include('deleteram.urls')),
    path('upload/', include('upload.urls')),
    path('deletefile/', include('deletefile.urls')),
    path('deletebrain/', include('deletebrain.urls')),
    path('membrains/', include('membrains.urls')),
    path('chatbot/',include('chatbot.urls')),
    path('renamebrain/',include('renamebrain.urls')),
    path('testurl/', include('testurl.urls')),
]
