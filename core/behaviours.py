from django.db import models
from django.db.models import UniqueConstraint, constraints, CheckConstraint, Q
from django.db.models.fields.related import ManyToManyField, OneToOneField, ForeignKey

class Authorable(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def get_user(self):
        return self.user.id


class Followable(models.Model):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, null=True)
    followers = models.ManyToManyField("core.User", related_name="followers")

    class Meta:
        abstract = True
    
    def get_user(self):
        return self.user.id