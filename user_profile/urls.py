from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('updatephoto', views.updatephoto, name='updatephoto'),
    path('updateprivacy', views.updateprivacy, name='updateprivacy'),
    path('changepwd', views.changepwd, name='changepwd'),
]