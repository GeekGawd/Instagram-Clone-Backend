from django.contrib import admin
from django.contrib.admin.helpers import AdminField
from django.db import models
from socialuser.models import Bookmark, Comment, FollowRequest, Profile, Post, Image, Profile, Story, Video

# Register your models here.


class ImagesAdmin(admin.StackedInline):
    model = Image

class VideosAdmin(admin.StackedInline):
    model = Video
 
class PostAdmin(admin.ModelAdmin):
    inlines = [ImagesAdmin, VideosAdmin]

    class Meta:
        model = Post


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
admin.site.register(Story)