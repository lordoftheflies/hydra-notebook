"""hydra_notebook_site URL Configuration

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
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers

from . import views

urlpatterns = [
    path('list_notebooks/', views.list_notebooks, name='list_notebooks'),
    path('show_notebook/<str:fname>/', views.show_notebook, name='show_notebook'),

    url(r'^api/$', views.list_notebooks_json, name='list_notebooks_json'),
    url(r'^api/(?P<fname>\d+)/$', views.show_notebook_json, name='show_notebook_json'),
    url(r'^api/upload/(?P<filename>[^/]+)$', views.FileUploadView.as_view(), name='upload_notebook_file'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
