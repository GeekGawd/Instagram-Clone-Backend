from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from rest_framework import serializers
from core.models import *
import socialuser
from socialuser.models import Comment, FollowRequest, Post, Profile, Story, Image, Tag, Video


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
        fields = ['videos']


class ProfileViewSerializer(serializers.ModelSerializer):
    is_follow = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'profile_photo', 'bio', 'active_story',
                  'is_private', 'user', 'no_of_following', 'no_of_followers', 'is_follow']
        extra_kwargs = {'username': {'required': False}}

    def to_representation(self, instance):
        data = super(ProfileViewSerializer, self).to_representation(instance)
        data['user_name'] = instance.user.name
        
        return data

    def get_is_follow(self, instance):
        request = self.context.get("request")
        if self.context.get("request").method=="POST":
            user_id = request.data.get('user_id')
            request_user_profile = Profile.objects.get(
                                                user=User.objects.get(id=user_id)
                                            )
            session_user_profile = Profile.objects.get(user=request.user)
            if request_user_profile == session_user_profile:
                return None
            elif request_user_profile.followers.filter(id=request.user.id).exists():
                return True
            else:
                return False


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
    post_like = LikePostSerializer(source="post_set", many=True)
    comment_like = LikeCommentSerializer(source="comment_set", many=True)

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
        fields = ['post_image', 'post_video',
                  'caption', 'user', 'no_of_likes', 'id']

    def to_representation(self, instance):
        data = super(PostViewSerializer, self).to_representation(instance)
        post_id = data.pop('id')
        data['post_id'] = post_id
        data['user_name'] = instance.user.name
        return data


class HomeFeedStorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['profile_photo', 'active_story', 'user', 'username']


class TagSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'tag', 'no_of_posts']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("no_of_posts")==0:
            instance.delete()
            data.update({"id":None,"tag": None,"no_of_posts": None})
        return data


class ProfileSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        exclude = ['followers', 'bio', 'is_private']

    def to_representation(self, instance):
        data = super(ProfileSearchSerializer, self).to_representation(instance)
        data['user_name'] = instance.user.name
        return data
