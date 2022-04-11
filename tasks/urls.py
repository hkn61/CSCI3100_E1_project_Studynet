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
    path('showfinishedtask', views.showfinishedtask, name="showfinishedtask"),
    path('showdeletedtask', views.showdeletedtask, name="showdeletedtask"),
    path('getfinishedtask', views.getfinishedtask, name="getfinishedtask"),
    path('getdeletedtask', views.getdeletedtask, name="getdeletedtask"),
    path('changefinishedstatus', views.changefinishedstatus, name="changefinishedstatus"),
    path('restorefinishedtask', views.restorefinishedtask, name="restorefinishedtask"),
    path('restoredeletetask', views.restoredeletetask, name="restoredeletetask"),

    path('timer', views.timer, name="timer"),

]
