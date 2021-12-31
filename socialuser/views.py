import re
from core.models import User
from django.db import models
from rest_framework import generics
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from socialuser.models import Profile, Post
from socialuser.serializers import ImageSerializer, PostSerializer, PostViewSerializer, ProfileViewSerializer, VideoSerializer

# Create your views here.


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = PostSerializer

    def get(self, request):
        user = request.user
        serializer = PostViewSerializer(
            Post.objects.filter(user=user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            post = serializer.save()
        else:
            return Response(
                {"status": "Error: Post couldn't be created"}, status.HTTP_400_BAD_REQUEST)

        try:
            images = dict((request.data).lists())['images']
            flag1 = True
        except KeyError:
            flag1 = False
        try:
            videos = dict((request.data).lists())['videos']
            flag2 = True
        except KeyError:
            flag2 = False

        if flag1:
            for img in images:
                imgdict = {"post": post.id, "images": img}
                serializer1 = ImageSerializer(data=imgdict)
                if serializer1.is_valid():
                    serializer1.save()
                else:
                    return Response(
                        serializer1.errors,
                        status=status.HTTP_400_BAD_REQUEST)
        if flag2:
            for vdo in videos:
                videodict = {"post": post.id, "videos": vdo}
                serializer2 = VideoSerializer(data=videodict)
                if serializer2.is_valid():
                    serializer2.save()
                else:
                    return Response(
                        serializer2.errors,
                        status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': "Post created."}, status=status.HTTP_201_CREATED)

class PostView(generics.ListAPIView):
    model = Post
    serializer_class = PostViewSerializer

    def get_queryset(self):
        posts = []
        for follower in Profile.objects.get_followers(self.request):
            posts.append(Post.objects.get(user=follower))
        return posts


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
        data["following"] = len(session_user_profile.followers.all())
        data["followers"] = len(request.user.followers.all())

        if session_user_profile.followers.filter(id=pk).exists():
            data["is_follow"] = True
        arr = {"profile": data, "posts": serializer2}
        return Response(arr, status=status.HTTP_200_OK)

class ProfileUpdateView(generics.RetrieveUpdateDestroyAPIView):
    model = Profile
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileViewSerializer
    queryset = Profile.objects.all()
