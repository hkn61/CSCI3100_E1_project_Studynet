from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('updatephoto', views.updatephoto, name='updatephoto'),
    path('changepwd', views.changepwd, name='changepwd'),
]