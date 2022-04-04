from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('group',views.group,name='group'),
    path('groupadd',views.groupadd,name='groupadd'),
    path('grouplist',views.grouplist,name='grouplist'),
    re_path(r'^(?P<room_name>[^/]+)/$', views.groupchat, name='groupchat'),
]
