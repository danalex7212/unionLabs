from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class OpenPorts(models.Model):
    port = models.IntegerField()
    def __str__(self):
        return self.port

class UsedPorts(models.Model):
    port = models.IntegerField()
    def __str__(self):
        return self.port

class OpenInstance(models.Model):
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)
    #port = models.ForeignKey(UsedPorts)
    #user = models.ForeignKey(User)
    machine = models.BinaryField(null=True)
    def __str__(self):
        return self.name

class UsedInstance(models.Model):
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)
    #port = models.ForeignKey(UsedPorts)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine = models.BinaryField(null=True)
    def __str__(self):
        return self.name