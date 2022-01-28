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

class PddUser(models.Model):
    objects = models.Manager()
    
    uid = models.CharField(max_length=64)
    ip = models.CharField(max_length=64)
    ua1 = models.CharField(max_length=255)
    ua2 = models.CharField(max_length=255)
    down_times = models.SmallIntegerField(default=5)
    time = models.DateTimeField(auto_now=True)
    update_time = models.CharField(max_length=8)

class PddVideo(models.Model):
    objects = models.Manager()
    url = models.CharField(max_length=255)
    feed_id = models.CharField(max_length=255)
    goods_id = models.CharField(max_length=255)
    likes = models.CharField(max_length=255)
    comments = models.CharField(max_length=255)
    publish_time = models.DateTimeField()
    down_time = models.DateTimeField(auto_now=True)

class AllowedRgisterUser(models.Model):
    '''
    允许注册的用户
    '''
    objects = models.Manager()
    uid = models.CharField(max_length=32)

