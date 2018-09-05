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
    path('view/native/notebooks/', views.list_notebooks, name='list_notebooks'),
    path('view/native/notebook/<str:name>/', views.notebook_html, name='show_notebook'),

    path('script/native/notebook/<str:name>/', views.notebook_script, name='notebook_script'),
    path('script/native/notebook/download/<str:name>/', views.notebook_script_download, name='notebook_script_download'),

    url(r'^api/native/notebooks/$', views.list_notebooks_json, name='list_notebooks_json'),
    url(r'^api/native/notebook/(?P<name>[^/]+)$', views.show_notebook_json, name='show_notebook_json'),
    url(r'^api/native/notebook/upload/(?P<filename>[^/]+)$', views.FileUploadView.as_view(), name='upload_notebook_file'),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
