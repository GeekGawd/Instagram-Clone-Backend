from django.db import models
from django.db.models import UniqueConstraint, constraints, CheckConstraint, Q
from django.db.models.fields.related import ManyToManyField, OneToOneField, ForeignKey
from django.utils import timezone


class Authorable(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    def get_user(self):
        return self.user.id


class Followable(models.Model):
    followers = models.ManyToManyField("core.User", related_name="followers")

    class Meta:
        abstract = True
    
    def get_user(self):
        return self.user.id

class Bookmarkable(models.Model):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, null=True, blank=True)
    posts = models.ManyToManyField("socialuser.Post")

    class Meta:
        abstract = True
    

class Creatable(models.Model):
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True