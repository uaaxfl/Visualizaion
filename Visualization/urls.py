"""Visualization URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from Controller.views import search, index, update, download_picture, showlist, index_id, download_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', search),
    path('index/', index),
    path('update/', update),
    path('download/', download_picture),
    path('showlist/', showlist),
    url(r'^index_alt/([0-9]+)', index_id),
    url(r'^picture/id=(?P<id>[0-9]+)&mode=(?P<mode>(0|1))&isKeyPaper=(?P<isKeyPaper>(0|1|0+(.[1-9])))&extends_prob=(?P<extends_prob>(0|1|0+(.[1-9])))/', download_detail),
]
