import re
from django.db.models import fields, UniqueConstraint
from django.db.models.base import Model
from django.db.models.fields import BooleanField, TextField
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField
from core.behaviours import *
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator


class FollowManager(models.Manager):

    def get_following(self, request):
        return self.get(user=request.user).user.followers.all()


class StoryManager(models.Manager):

    def get_story(self, request):
        return self.exclude(Q(profile=Profile.objects.get(user=request.user)) | Q(is_expired=True)).order_by('-id')


class TagManager(models.Manager):

    def extract_hashtags(self, post, text):

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
        return request_user_profile.followers.filter(email=session_user_profile.user.email).exists() or not request_user_profile.is_private or session_user_profile == request_user_profile


class Post(Authorable, Creatable, Model):
    caption = TextField(max_length=350, null=True, blank=True)
    liked_by = ManyToManyField(
        "core.User", related_name="like_post", blank=True)

    objects = PostManager()

    def __str__(self) -> str:
        return f"{self.user.email} posted {self.caption}"

    def no_of_likes(self):
        return self.liked_by.count()

# class Media(Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # media = models.URLField(max_length=200)


class Comment(Creatable, Model):
    liked_by = ManyToManyField(
        "core.User", related_name="like_comment", blank=True)
    content = TextField(max_length=250)
    comment_by = ForeignKey("core.User", on_delete=models.CASCADE,related_name="comment_by")
    post = ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="postcomments")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        if self.parent is None:
            return f"{self.comment_by.name} -> {self.content[:35]}"
        return f"{self.parent.content[:35]} -> {self.comment_by.name} -> {self.content[:35]}"
    
    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


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
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, null=True, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        ('username'),
        max_length=150,
        unique=True,
        help_text=(
            'Required. 150 characters or fewer. Letters, digits and _/. only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    profile_photo = models.URLField(null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    is_private = models.BooleanField(default=False)     

    objects = FollowManager()

    def __str__(self) -> str:
        return f"{self.user.email} Profile -> {self.username}"

    def no_of_following(self):
        return self.user.followers.count()

    def no_of_followers(self):
        return self.followers.count()
    
    @property
    def home_active_story(self):
        no_of_active_story = len(self.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1)))
        no_of_unseen_story = len(self.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1), is_seen = False))
        if no_of_active_story > 0 and no_of_unseen_story>0:
            return 2
        elif no_of_active_story > 0:
            return 1
        else:
            return 0

class Bookmark(Bookmarkable, Model):
    pass

    def __str__(self) -> str:
        return f"{self.user.email}'s Bookmark"


class FollowRequest(Model):
    from_user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="to_user")
    
    def __str__(self) -> str:
        return f"Follow Request from {self.from_user.email}->{self.to_user.email}"


class Story(Creatable, Model):
    user = ForeignKey("core.User", on_delete=models.CASCADE, related_name="userstory")
    is_seen = models.BooleanField(default=False)

    objects = StoryManager()

    def __str__(self) -> str:
        return f"Story posted by {self.user.email}"


class Tag(models.Model):
    post = ManyToManyField(Post, related_name="tag_post")
    tag = models.CharField(max_length=30, unique=True, blank=True, null=True)

    objects = TagManager()

    def __str__(self):
        return f"#{self.tag}"

    def no_of_posts(self):
        return len(self.post.all())

class Image(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, blank=True, null=True)
    images = models.URLField(max_length=200)

    def __str__(self) -> str:
        if self.post is not None:
            return f"Post ID {self.post.id} ->{self.images}"
        return f"Story ID {self.story.id} ->{self.images}"


class Video(Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, blank=True, null=True)
    videos = models.URLField(max_length=200)

    def __str__(self) -> str:
        if self.post is not None:
            return f"Post ID {self.post.id} ->{self.videos}"
        return f"Story ID {self.story.id} ->{self.videos}"
