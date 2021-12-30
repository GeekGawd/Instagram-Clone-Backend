from django.db import models
from django.db.models.fields.related import OneToOneField, ForeignKey
from core.models import User
class Authorable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
    
    def get_user(self):
        return self.user.id