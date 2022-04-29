from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('group', views.group, name='group'),
    path('groupadd', views.groupadd, name='groupadd'),
    path('groupcreate', views.groupcreate, name='groupcreate'),
    path('groupsearch', views.groupsearch, name='groupsearch'),
    path('grouplist', views.grouplist, name='grouplist'),
    path('<str:room_name>/', views.groupchat, name='groupchat'),
    path('historysearch', views.historysearch, name='historysearch'),
]
