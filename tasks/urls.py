from django.contrib import admin

from django.urls import path, include
from django.views.generic import TemplateView

from . import views
urlpatterns = [
    # Task
    path('tasklist', views.tasklist, name='signup'),
    path('gettasklist', views.gettasklist, name="gettasklist"),
    path('inserttask', views.inserttask, name="inserttask"),
    path('deletetask', views.deletetask, name="deletetask"),
    path('changedoingstatus', views.changedoingstatus, name="changedoingstatus"),

    # Finished task
    path('showfinishedtask', views.showfinishedtask, name="showfinishedtask"),
    path('getfinishedtask', views.getfinishedtask, name="getfinishedtask"),
    path('restorefinishedtask', views.restorefinishedtask, name="restorefinishedtask"),


    # Deleted task
    path('showdeletedtask', views.showdeletedtask, name="showdeletedtask"),
    path('getdeletedtask', views.getdeletedtask, name="getdeletedtask"),
    path('restoredeletetask', views.restoredeletetask, name="restoredeletetask"),

    # Timer
    path('timer', views.timer, name="timer"),
    path('changefinishedstatus', views.changefinishedstatus, name="changefinishedstatus"),
    path('getdoinglist', views.getdoinglist, name="getdoinglist"),
    path('addtimespent', views.addtimespent, name="addtimespent"),

    # Report
    path('report', views.report, name="report"),
    path('get_report_data', views.get_report_data, name="get_report_data"),
]
