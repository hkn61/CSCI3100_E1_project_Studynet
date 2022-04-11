from distutils.command.upload import upload
from django.db import models
import os
# Create your models here.

def filepath(request, username):
    filename = username
    return os.path.join('profiles/', filename)

'''
class Image(models.Model):
    class Meta:
        app_label = 'django.contrib.auth'
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='static/form', default='default.png')

'''
MEDIA_ADDR = 'http://localhost:8011/media/'

class Image(models.Model):
    class Meta:
        app_label = 'profile'
        db_table = 'Image'

    username = models.TextField(max_length=100)
    #email = models.TextField(max_length=100)
    image = models.ImageField(upload_to='avatar', null=True, blank=True, default='default.png')

