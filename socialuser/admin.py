from django.contrib import admin
from django.contrib.admin.helpers import AdminField
from django.db import models
from django.forms import fields
from socialuser.models import Bookmark, Comment, FollowRequest, Profile, Post, Image, Profile, Story, Tag, Video

# Register your models here.


class ImagesAdmin(admin.StackedInline):
    model = Image
    fields = ('images',)

class VideosAdmin(admin.StackedInline):
    model = Video
    fields = ('videos',)
 
class PostAdmin(admin.ModelAdmin):
    inlines = [ImagesAdmin, VideosAdmin]

    class Meta:
        model = Post

class StoryAdmin(admin.ModelAdmin):
    inlines = [ImagesAdmin, VideosAdmin]

    class Meta:
        model = Story


class ImagesAdmin(admin.ModelAdmin):
    pass


class VideosAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImagesAdmin)
admin.site.register(Video, VideosAdmin)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Bookmark)
admin.site.register(FollowRequest)
admin.site.register(Story, StoryAdmin)
admin.site.register(Tag)