from django.contrib import admin

from django.urls import path, include
from django.views.generic import TemplateView

from . import views
urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('send_email', views.send_email, name='send_email'),
]
