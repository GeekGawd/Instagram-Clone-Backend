import re
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.db.models.fields import BooleanField, CharField, TextField
from django.db.models.fields.related import OneToOneField
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from socialuser.models import Profile
from core.behaviours import Authorable


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        Profile.objects.create(user=user)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def tokens(self):
        refresh=RefreshToken.for_user(self)
        return{
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def refresh(self):
        refresh=RefreshToken.for_user(self)
        return str(refresh)
    
    def access(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh.access_token)

    def get_name(self):
        return str(self.name)

class OTP(models.Model):
    otp = models.IntegerField()
    otp_email = models.EmailField()
    time_created = models.IntegerField()
    
    def __str__(self):
        return f"{self.otp_email} : {self.otp}"

class Notification(Authorable, models.Model):
    notification = models.TextField(max_length=250)

    def __str__(self) -> str:
        return f"{self.user}-->{self.notification}"