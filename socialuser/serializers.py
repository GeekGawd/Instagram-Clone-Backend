from rest_framework import serializers
from core.models import *
from socialuser.models import *
from django.core.exceptions import ObjectDoesNotExist

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

        print(image_data, video_data, sep="\n")
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

# class ImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Images
#         fields = [ 'post','images']

class ImageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['images']

# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Videos
#         fields = [ 'post','videos']

class VideoViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [ 'videos']

class PostViewSerializer(serializers.ModelSerializer):
    Like = serializers.SerializerMethodField()
    post_image = ImageViewSerializer(many=True, source='image_set')
    post_video = VideoViewSerializer(many=True, source='video_set')
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['post_image', 'post_video',
                  'caption', 'user', 'no_of_likes',
                   'id', 'Like', 'bookmarked']

    def to_representation(self, instance):
        data = super(PostViewSerializer, self).to_representation(instance)
        post_id = data.pop('id')
        data['post_id'] = post_id
        data['user_name'] = instance.user.name
        data['profile_picture'] = instance.user.profile.profile_photo
        return data

    def get_Like(self, instance):
        request = self.context.get("request")
        user = request.user
        try:
            instance.liked_by.get(id=user.id)
            return True
        except ObjectDoesNotExist:
            return False
    
    def get_bookmarked(self, instance):
        return False