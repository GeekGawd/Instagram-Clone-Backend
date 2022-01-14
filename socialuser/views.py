import re
from django.db.models import query, Q
from django.http import request
from rest_framework import permissions
from chat import api
from core.models import User
from django.db import models
from rest_framework import generics, mixins
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from socialuser.models import Comment, Profile, Post, FollowRequest, Story, Image, Video
from socialuser.serializers import CommentSerializer, FollowRequestSerializer, FollowRequestSerializer,\
     FollowerViewSerializer, HomeFeedStorySerializer,\
     LikePostSerializer, LikeSerializer, PostSerializer, PostViewSerializer,\
     ProfileViewSerializer, StorySerializer

# Create your views here.


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request):
        photos = request.data['photos']
        videos = request.data['videos']
        try:
            request.data['user'] = request.user.id
        except:
            return Response({"status": "User not registered."},status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
        
        if photos is None and videos is None:
            return Response({"status": "Cannot create post with no media."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if photos is None:
            photos = []

        if videos is None:
            videos = []

        if isinstance(photos, list):
            img = [Image(post=post, images=photo) for photo in photos]
            Image.objects.bulk_create(img)

        if isinstance(videos, list):
            vdo = [Video(post=post, videos=video) for video in videos]
            Video.objects.bulk_create(vdo)

        return Response({"status": "Post successfully created."},status=status.HTTP_201_CREATED)
        
class PostView(generics.GenericAPIView, mixins.ListModelMixin):
    model = Post
    serializer_class = PostViewSerializer

    def get_queryset(self):
        posts = []
        for follower in Profile.objects.get_followers(self.request):
            try:
                Post.objects.get(user=follower)
                posts.append(Post.objects.get(user=follower))
            except:
                pass
        return posts
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)        


class ProfileView(APIView):

    def get(self, request, pk):
        request_user_profile, _ = Profile.objects.get_or_create(user=pk)
        session_user_profile, _ = Profile.objects.get_or_create(
            user=self.request.user)
        serializer1 = ProfileViewSerializer(request_user_profile)
        try:
            serializer2 = PostViewSerializer(
                Post.objects.filter(user=pk), many=True).data
        except:
            serializer2 = {"posts": None}

        data = serializer1.data
        data["is_follow"] = False
        data["following"] = len(request_user_profile.followers.all())
        data["followers"] = len(request_user_profile.user.followers.all())

        if session_user_profile.followers.filter(id=pk).exists():
            data["is_follow"] = True
        arr = {"profile": data, "posts": serializer2}
        return Response(arr, status=status.HTTP_200_OK)
    
class UserProfileChangeAPIView(generics.GenericAPIView,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileViewSerializer

    def get_object(self):
        obj = Profile.objects.get(user=self.request.user)
        return obj
    
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class FollowerCreateView(APIView):
    serializer_class = FollowerViewSerializer
    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        user_id = request.data.get("user_id")
        request_user_profile, _ = Profile.objects.get_or_create(user=User.objects.get(id=user_id))
        if profile.followers.filter(pk=request_user_profile.user.id).exists():
            profile.followers.remove(request_user_profile.user)
            return Response("User Unfollowed")
            
        elif not request_user_profile.is_private:
            profile.followers.add(request_user_profile.user)
            return Response("User followed")
        
        else:
            try: 
                follow_request = FollowRequest.objects.get(from_user=request.user,
                                to_user=request_user_profile.user)
                follow_request.delete()
                return Response({"status": "Follow Request Removed."})
            except:
                FollowRequest.objects.create(from_user=request.user,
                                        to_user=request_user_profile.user)
                return Response({"status":"Follow Request Sent to User"})

class FollowRequestView(APIView):
    serializer_class = FollowRequestSerializer
    def get(self, request):
        follow_request = FollowRequest.objects.filter(to_user=request.user)
        try:
            serializer = self.serializer_class(follow_request, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"status": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        follow_id = request.data.get("follow_id")
        confirmation = request.data.get("confirm")
        try:
            follow_request = FollowRequest.objects.get(id=follow_id)
        except:
            return Response({"status": "No Follow Request has been sent."})
        
        if confirmation.casefold() == "true":
            Profile.objects.get(user=request.user).followers.add(follow_request.from_user)
            follow_request.delete() 
            return Response({"status": "Follow Request Accepted."})
        elif confirmation.casefold() == "false":
            follow_request.delete()
            return Response({"status": "Follow Request Rejected."})
        else:
            return Response({"status": "Enter a valid confirmation."})

class StoryView(generics.GenericAPIView, mixins.ListModelMixin, mixins.DestroyModelMixin):
    serializer_class = StorySerializer

    def get_queryset(self):
        try:
            user_id = self.request.data['user_id']
        except:
            return Response({"Enter a user id to view story."}, status=status.HTTP_400_BAD_REQUEST)
        return Story.objects.filter(profile=Profile.objects.get(user=user_id), is_expired=False).order_by('-id')
    
    def get_object(self):
        try:
            story_id = self.request.data['story_id']
        except:
            return Response({"Enter story id to delete story."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Story.objects.get(id=story_id)

    def get(self, request, *args, **kwargs):
        return super().list  (request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class HomeStoryView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = HomeFeedStorySerializer

    def get_queryset(self):
        qs = Story.objects.get_story(self.request)
        stories = [story.profile for story in qs]
        return stories

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class LikeView(APIView):
    
    def put(self, request):
        
        post_id = request.data.get("post_id")
        comment_id = request.data.get("comment_id")
        post = Post.objects.filter(id=post_id).first()
        comment = Comment.objects.filter(id=comment_id).first()

        if not post and not comment:
            return Response({"status": "Enter a post/comment id to like"})
        
        if post:
            try:
                post.liked_by.get(id=request.user.id)
                post.liked_by.remove(request.user)
                return Response({"status": "Post Unliked Successfully."}, status=status.HTTP_202_ACCEPTED)
            except:
                post.liked_by.add(request.user)
                return Response({"status": "Post Liked Successfully."}, status=status.HTTP_201_CREATED)
        
        if comment:
            try:
                comment.liked_by.get(id=request.user.id)
                comment.liked_by.remove(id=request.user.id)
                return Response({"status": "Post UnLiked Successfully."}, status=status.HTTP_202_ACCEPTED)
            except:
                comment.liked_by.add(request.user)
                return Response({"status": "Post Liked Successfully."}, status=status.HTTP_201_CREATED)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer