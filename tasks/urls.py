from django.contrib import admin

from django.urls import path, include
from django.views.generic import TemplateView

from . import views
urlpatterns = [
    path('tasklist', views.tasklist, name='signup'),
    path('report', views.report, name="report"),

]
