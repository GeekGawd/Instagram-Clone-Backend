from django.contrib import admin
from django.contrib.admin.helpers import AdminField
from django.db import models
from socialuser.models import Comments, Likes, Post, Images, Videos

# Register your models here.

class ImagesAdmin(admin.StackedInline):
    model = Images

class VideosAdmin(admin.StackedInline):
    model = Videos
 
class PostAdmin(admin.ModelAdmin):
    inlines = [ImagesAdmin, VideosAdmin]
 
    class Meta:
       model = Post

class ImagesAdmin(admin.ModelAdmin):
    pass

class VideosAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Videos, VideosAdmin)
admin.site.register(Comments)
admin.site.register(Likes)