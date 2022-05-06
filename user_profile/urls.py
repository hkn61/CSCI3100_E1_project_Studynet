from django.contrib import admin
from django.urls import path, include
from . import views

# match or capture a value from the URL and invoke functions in views.py accordingly
urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('updatephoto', views.updatephoto, name='updatephoto'),
    path('updateprivacy', views.updateprivacy, name='updateprivacy'),
    path('changepwd', views.changepwd, name='changepwd'),
]