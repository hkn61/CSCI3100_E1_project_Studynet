from distutils.command.upload import upload
from django.db import models
import os
# Create your models here.

def filepath(request, username):
    filename = username
    return os.path.join('profiles/', filename)


class UserModel(models.Model):
    class Meta:
        app_label = 'django.contrib.auth'

    username = models.TextField(max_length=100)
    email = models.TextField(max_length=100)
    image = models.ImageField(upload_to=filepath, null=True, blank=True, default='default.png')
