from django.contrib import admin

from django.urls import path, include
from django.views.generic import TemplateView

from . import views
urlpatterns = [
    path('tasklist', views.tasklist, name='signup'),
    path('report', views.report, name="report"),
    path('gettasklist', views.gettasklist, name="gettasklist"),
    path('inserttask', views.inserttask, name="inserttask"),
    path('deletetask', views.deletetask, name="deletetask"),

]
