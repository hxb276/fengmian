from enum import auto
from operator import mod
from django.db import models

# Create your models here.
class MyUser(models.Model):
    object = models.Manager()

    ip = models.CharField(max_length=64)
    access_time = models.DateTimeField(auto_now=True)

class Xuliehao(models.Model):
    object = models.Manager()
    number = models.CharField(max_length=128)
    status = models.CharField(max_length=1,default=1)