"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import url
from django.urls import path
from django.conf.urls import include

from password.views import *
from testapp.views import *

urlpatterns = [
    path('', table),
    # path('', login_required(table)),
    path('password/', include('password.urls')),
    path('login', mylogin, name='login'),
    path('regist', myregist, name='regist'),

]
