import re
from statistics import mode
from tkinter.tix import Tree
from django.db.models import fields, UniqueConstraint
from django.db.models.base import Model
from django.db.models.fields import BooleanField, TextField
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField
from core.behaviours import *
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator

class FollowManager(models.Manager):

    def get_followers(self, request):
        return self.exclude(followers=request.user).get(user=request.user).followers.all()

class StoryManager(models.Manager):

    def get_story(self, request):
        return self.exclude(Q(profile=Profile.objects.get(user=request.user)) | Q(is_expired=True)).order_by('-id')

class TagManager(models.Manager):

    def extract_hashtags(self,post,text):
     
        # the regular expression
        regex = "#(\w+)"
        
        # extracting the hashtags
        hashtag_list = re.findall(regex, text)
        hashtag_list = set(hashtag_list)
        for hashtag in hashtag_list:
           tag, _ = Tag.objects.get_or_create(tag=hashtag)
           tag.post.add(post)


class PostManager(models.Manager):

    def post_authorization(self, request_user_profile, session_user_profile):
        return request_user_profile.followers.filter(email=session_user_profile.user.email).exists() or not request_user_profile.is_private or session_user_profile==request_user_profile


class Post(Authorable,Creatable, Model):
    caption = TextField(max_length=350, null=True, blank=True)
    liked_by = ManyToManyField("core.User", related_name="like_post", blank=True)
    # tag = ManyToManyField(Tag, blank=True)

    objects = PostManager()

    def no_of_likes(self):
        return len(self.liked_by.all())

class Image(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    images = models.URLField(max_length=200)

class Video(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    videos = models.URLField(max_length=200)

# class Media(Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # media = models.URLField(max_length=200)

class Comment(Model):
    liked_by = ManyToManyField("core.User", related_name="like_comment", blank=True)
    comment = TextField(max_length=250)
    comment_by = ForeignKey("core.User", on_delete=models.CASCADE)
    post = ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment_by.name} -> {self.comment[:35]}"


# class Like(Model):
#     liked_by = ForeignKey("core.User", on_delete=models.CASCADE, null=True)
#     post = ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
#     comment = ForeignKey(Comment, on_delete=models.CASCADE,
#                          null=True, blank=True)

#     class Meta:
#         constraints = [
#             UniqueConstraint(
#                 name='unique_like',
#                 fields=['liked_by', 'post']
#             ),
#             UniqueConstraint(
#                 name='unique_comment',
#                 fields=['liked_by', 'comment']
#             )
#         ]


class Profile(Followable, Model):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE,null=True, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        ('username'),
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, digits and _/. only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    profile_photo = models.ImageField(blank = True, default="default-user-icon-13.jpg")
    bio = models.CharField(max_length=150, null=True, blank=True)
    active_story = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    objects = FollowManager()

class Bookmark(Bookmarkable, Model):
    pass

class FollowRequest(Model):
    from_user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="to_user")

class Story(Creatable,Model):
    profile = ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.FileField(upload_to="story/")
    is_expired = models.BooleanField(default=False)

    objects = StoryManager()

class Tag(models.Model):
    post = ManyToManyField(Post, related_name="tag_post")
    tag = models.CharField(max_length=30, unique=True, blank=True, null=True)

    objects = TagManager()
    
    def __str__(self):
        return f"#{self.tag}"
    
    def no_of_posts(self):
        return len(self.post.all())