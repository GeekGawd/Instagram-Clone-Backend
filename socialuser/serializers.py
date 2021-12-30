from rest_framework import serializers
from core.models import *
from socialuser.models import Images, Post, Videos

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [ 'caption','user']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = [ 'post','images']

class ImageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['images']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = [ 'post','videos']

class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = [ 'videos']

class PostViewSerializer(serializers.ModelSerializer):
    #           access ForeignKey in reverse 🖟
    post_image = ImageViewSerializer(source='images_set', many=True)
    post_video = VideoViewSerializer(source='videos_set', many=True)
    
    class Meta:
        model = Post
        fields = ['post_image', 'post_video', 'caption','user']