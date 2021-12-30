import re
from django.shortcuts import render, resolve_url
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from socialuser.models import Post

from socialuser.serializers import ImageSerializer, PostSerializer, PostViewSerializer, VideoSerializer

# Create your views here.

class PostUpload(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = PostSerializer
    
    def get(self, request):
        user = request.user
        serializer = PostViewSerializer(Post.objects.filter(user=user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        user = request.user
        data = request.data
        data['user']=request.user.id
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