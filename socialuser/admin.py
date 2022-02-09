from django.contrib import admin
from django.contrib.admin.helpers import AdminField
from django.db import models
from socialuser.models import Profile, Post, Image, Profile, Video, Comments, Likes

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


class ImagesAdmin(admin.ModelAdmin):
    pass
class VideosAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImagesAdmin)
admin.site.register(Video, VideosAdmin)
admin.site.register(Comments)
admin.site.register(Likes)
admin.site.register(Profile)