from cmath import isnan
from django.db.models import fields
from django.db.models.fields.related import ForeignKey
from rest_framework import serializers
from core.models import *
import socialuser
from socialuser.models import Comment, FollowRequest, Post, Profile, Story, Image, Tag, Video
from rest_framework.fields import empty


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
    active_story = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'profile_photo', 'bio', 'active_story',
                  'is_private', 'user', 'no_of_following', 'no_of_followers',
                  'is_follow', 'follow']
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
    
    def get_active_story(self, instance):
        request = self.context.get("request")
        if self.context.get("request").method=="POST":
            request = self.context.get("request")
            user_id = request.data.get("user_id")
            request_user_profile = Profile.objects.get(user=user_id)
            session_user_profile = Profile.objects.get(user=request.user.id)
            no_of_active_story = len(instance.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1)))
            no_of_unseen_story = len(instance.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1), is_seen = False))
            if no_of_active_story > 0 and no_of_unseen_story>0 and Post.objects.post_authorization(request_user_profile, session_user_profile):
                return 2
            elif no_of_active_story > 0 and Post.objects.post_authorization(request_user_profile, session_user_profile):
                return 1
            else:
                return 0
    def get_follow(self, instance):
        if self.context.get("request").method=="POST":
            request = self.context.get("request")
            user_id = request.data.get("user_id")
            request_user_profile = Profile.objects.get(user=user_id)
            session_user_profile = Profile.objects.get(user=request.user.id)
            if FollowRequest.objects.filter(to_user=request_user_profile.user,
                                                from_user=session_user_profile.user).exists() or request_user_profile.followers.filter(id=request.user.id).exists():
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
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile_from_user = Profile.objects.get(user=instance.from_user)
        profile_to_user = Profile.objects.get(user=instance.to_user)
        data['from_user_username']=profile_from_user.username
        data['to_user_username']=profile_to_user.username
        data['from_user_profile_photo']=profile_from_user.profile_photo
        data['to_user_profile_photo']=profile_to_user.profile_photo
        return data


    

class StorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Story
        exclude = ['created_at']

    def create(self, validated_data):
        image_data = self.initial_data.get('photos')
        video_data = self.initial_data.get('videos')
        story = Story.objects.create(**validated_data)

        if image_data is not None and isinstance(image_data, list):
            images = [Image(story=story, images=photo) for photo in image_data]
            Image.objects.bulk_create(images)
        elif image_data is not None and isinstance(image_data, str):
            Image.objects.create(story=story, images=image_data)

        if video_data is not None and isinstance(video_data, list):
            videos = [Video(story=story, videos=video) for video in video_data]
            Video.objects.bulk_create(videos)
        elif video_data is not None and  isinstance(video_data, str):
            Video.objects.create(story=story, videos=video_data)
        
        return story

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
        fields = ['comment', 'comment_by', 'post']

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
        fields = ['profile_photo', 'home_active_story', 'user', 'username']


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

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['caption', 'user']
        extra_kwargs = {
            'user': {'required': True},
            'caption': {'required': False}
        }
    
    def create(self, validated_data):
        image_data = self.initial_data.get('photos')
        video_data = self.initial_data.get('videos')
        post = Post.objects.create(**validated_data)
        caption = validated_data.pop('caption', None)

        if image_data is not None and isinstance(image_data, list):
            images = [Image(post=post, images=photo) for photo in image_data]
            Image.objects.bulk_create(images)
        elif image_data is not None and isinstance(image_data, str):
            Image.objects.create(post=post, images=image_data)

        if video_data is not None and isinstance(video_data, list):
            videos = [Video(post=post, videos=video) for video in video_data]
            Video.objects.bulk_create(videos)
        elif video_data is not None and  isinstance(video_data, str):
            Video.objects.create(post=post, videos=video_data)

        Tag.objects.extract_hashtags(post, caption)
        
        return post

class StoryViewSerializer(serializers.ModelSerializer):
    post_image = ImageViewSerializer(many=True, source='image_set')
    post_video = VideoViewSerializer(many=True, source='video_set')

    class Meta:
        model = Story
        fields = ['post_image', 'post_video','is_seen',
                    'user', 'id']

    def to_representation(self, instance):
        data = super(StoryViewSerializer, self).to_representation(instance)
        data['user_name'] = instance.user.profile.username
        data['profile_picture'] = instance.user.profile.profile_photo
        return data