from django.db.models.base import Model
from django.db.models.fields import BooleanField, TextField
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField
from core.behaviours import *
from django.utils import timezone

class Post(Authorable, Model):
    created_at = models.DateTimeField(default=timezone.now)
    caption = TextField(max_length=350)

class Images(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    images = models.FileField(upload_to="images/")

class Videos(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    videos = models.FileField(upload_to="videos/")

class Comments(Model):
    comment = TextField(max_length=250)
    comment_by = ForeignKey(User, on_delete=models.CASCADE)
    post = ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment_by.name} -> {self.comment[:35]}"

class Likes(Model):
    like = BooleanField(default=False)
    liked_by = ForeignKey(User, on_delete=models.CASCADE)
    post = ManyToManyField(Post)
    comment = ManyToManyField(Comments)