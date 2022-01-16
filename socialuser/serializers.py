from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from rest_framework import serializers
from core.models import *
import socialuser
from socialuser.models import Comment, FollowRequest, Post, Profile, Story, Image, Video


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption', 'user']
        extra_kwargs = {
            'caption': {'required': False}
        }


# class ImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Image
#         fields = [ 'post','images']

class ImageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['images']


# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = [ 'post','videos']

class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ 'videos']

class ProfileViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        exclude = ['followers']
    
    def to_representation(self, instance):
        data =  super(ProfileViewSerializer, self).to_representation(instance)
        data['user_name'] = instance.user.name
        return data

class FollowerViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['followers']

class FollowRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowRequest
        fields = '__all__'

class StorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Story
        exclude = ['created_at']

class LikePostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = ['liked_by']

class LikeCommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['liked_by']

class LikeSerializer(serializers.Serializer):
    post_like = LikePostSerializer(source= "post_set",many=True)
    comment_like = LikeCommentSerializer(source = "comment_set",many=True)

    class Meta:
        fields = ['post_like', 'comment_like']

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'

# class MediaSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Media
#         fields = '__all__'

class PostViewSerializer(serializers.ModelSerializer):
    # comments = CommentSerializer(many=True, source='comment_set')
    # media = MediaSerializer(many=True, source='media_set')
    post_image = ImageViewSerializer(many=True, source='image_set')
    post_video = VideoViewSerializer(many=True, source='video_set')
    
    class Meta:
        model = Post
        fields = ['post_image','post_video','caption','user','no_of_likes', 'id']

    def to_representation(self, instance):
        data =  super(PostViewSerializer, self).to_representation(instance)
        post_id = data.pop('id')
        data['post_id'] = post_id
        data['user_name'] = instance.user.name
        return data

class HomeFeedStorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['profile_photo', 'active_story', 'user']

        