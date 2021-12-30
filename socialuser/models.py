from django.db.models import fields, UniqueConstraint
from django.db.models.base import Model
from django.db.models.fields import BooleanField, TextField
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField
from core.behaviours import *
from django.utils import timezone


class FollowManager(models.Manager):

    def get_followers(self, request):
        return self.exclude(followers=request.user).get(user=request.user).followers.all()


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
    comment_by = ForeignKey("core.User", on_delete=models.CASCADE)
    post = ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment_by.name} -> {self.comment[:35]}"


class Like(Model):
    liked_by = ForeignKey("core.User", on_delete=models.CASCADE, null=True)
    post = ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = ForeignKey(Comment, on_delete=models.CASCADE,
                         null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                name='unique_like',
                fields=['liked_by', 'post']
            ),
            UniqueConstraint(
                name='unique_comment',
                fields=['liked_by', 'comment']
            )
        ]


class Profile(Followable, Model):
    profile_photo = models.ImageField(blank = True, default="default-user-icon-13.jpg")
    bio = models.CharField(max_length=150, null=True, blank=True)
    active_story = models.BooleanField(default=False)
    
    objects = FollowManager()


class Bookmark(Bookmarkable, Model):
    pass
