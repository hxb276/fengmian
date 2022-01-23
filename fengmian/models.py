from os import access
from django.db import models

# Create your models here.
class MyUser(models.Model):
    objects = models.Manager()

    ip = models.CharField(max_length=64)
    xuliehao = models.CharField(max_length=128)
    access_time = models.DateTimeField(auto_now=True)

class AdCity(models.Model):
    objects = models.Manager()

    ip = models.CharField(max_length=64)
    access_time = models.DateTimeField(auto_now=True)
