from core.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.views.generic.list import ListView
from rest_framework import generics, mixins
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from socialuser.models import Comment, Profile, Post, FollowRequest, Story, Image, Video, Tag
from socialuser.serializers import CommentSerializer, FollowRequestSerializer, FollowRequestSerializer,\
    FollowerViewSerializer, HomeFeedStorySerializer,\
    LikePostSerializer, LikeSerializer, PostSerializer, PostViewSerializer, ProfileSearchSerializer,\
    ProfileViewSerializer, StorySerializer, TagSearchSerializer
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request):
        photos = request.data['photos']
        videos = request.data['videos']
        caption = request.data.get("caption")

        try:
            request.data['user'] = request.user.id
        except:
            return Response({"status": "User not registered."}, status=status.HTTP_401_UNAUTHORIZED)

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

        Tag.objects.extract_hashtags(post, caption)
        return Response({"status": "Post successfully created."}, status=status.HTTP_201_CREATED)


class HomePostView(generics.GenericAPIView, mixins.ListModelMixin):
    model = Post
    serializer_class = PostViewSerializer

    def get_queryset(self):
        posts = []
        # print(dir(Post.objects.select_related("user")))
        for follower in Profile.objects.get_following(self.request):
            try:
                for post in Post.objects.filter(user=follower.user):
                    posts.append(post)
            except:
                pass
        return posts

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# class ProfileView(APIView):

#     def get(self, request):
#         user_id = request.data.get("user_id")
#         if user_id:
#             try:
#                 request_user_profile, _ = Profile.objects.get_or_create(
#                     user=User.objects.get(id=user_id))
#             except:
#                 return Response({"status": "User doesn't exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#         else:
#             return Response({"status": "Enter a user_id"}, status=status.HTTP_400_BAD_REQUEST)
#         session_user_profile, _ = Profile.objects.get_or_create(
#             user=self.request.user)
#         serializer1 = ProfileViewSerializer(request_user_profile)
#         try:
#             serializer2 = PostViewSerializer(
#                 Post.objects.filter(user=user_id), many=True).data
#         except:
#             serializer2 = {"posts": None}

#         data = serializer1.data
#         if str(session_user_profile) != str(request_user_profile):
#             data["is_follow"] = False
#         data["following"] = len(request_user_profile.user.followers.all())
#         data["followers"] = len(request_user_profile.followers.all())

#         if Post.objects.post_authorization(request_user_profile, session_user_profile):
#             data["is_follow"] = True
#             arr = {"profile": data, "posts": serializer2}
#             return Response(arr, status=status.HTTP_200_OK)
#         else:
#             data["is_follow"] = None
#             arr = {"profile": data, "posts": "User Profile Private."}
#             return Response(arr, status=status.HTTP_206_PARTIAL_CONTENT)


class UserProfileAPIView(generics.GenericAPIView,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileViewSerializer

    def get_object(self):

        user_id = self.request.data.get("user_id")
        if self.request.method=="POST":
            obj = Profile.objects.get(user=user_id)
        else:
            obj = Profile.objects.get(user=self.request.user.id)

        return obj

    def post(self, request, *args, **kwargs):
        try:
            Profile.objects.get(user=request.data.get("user_id"))
        except ObjectDoesNotExist:
            return Response({"User is not registered"}, status=status.HTTP_400_BAD_REQUEST)
        return super().retrieve(request, *args, **kwargs)

    def delete(self, request):
        User.objects.get(id=request.user.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProfilePostView(generics.ListAPIView):
    serializer_class = PostViewSerializer

    def get_queryset(self):
        user_id = self.request.data.get("user_id")
        if user_id:
            try:
                request_user_profile = Profile.objects.get(
                    user=User.objects.get(id=user_id))
                session_user_profile = Profile.objects.get(
                    user=self.request.user)
            except:
                return Response({"status": "Request/Session User doesn't exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status": "Enter a user_id"}, status=status.HTTP_400_BAD_REQUEST)
        posts = Post.objects.filter(user=user_id)
        if Post.objects.post_authorization(request_user_profile, session_user_profile):
            return posts
        return None

    def post(self, request, *args, **kwargs):
        data = self.serializer_class(self.get_queryset(), many=True).data
        if len(data):
            return super().list(request, *args, **kwargs)
        return Response({"status": "Profile is Private"}, status=status.HTTP_403_FORBIDDEN)


class FollowerCreateView(APIView):
    serializer_class = FollowerViewSerializer

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        user_id = request.data.get("user_id")
        request_user_profile, _ = Profile.objects.get_or_create(
            user=User.objects.get(id=user_id))

        if user_id == request.user.id:
            return Response({"status": "You cannot follow yourself."}, status=status.HTTP_403_FORBIDDEN)
        if profile.followers.filter(id=request_user_profile.user.id).exists():
            profile.followers.remove(request_user_profile.user)
            return Response({"status": "User Unfollowed"}, status=status.HTTP_202_ACCEPTED)

        elif not request_user_profile.is_private:
            profile.followers.add(request_user_profile.user)
            return Response({"status": "User followed"}, status=status.HTTP_200_OK)

        else:
            try:
                follow_request = FollowRequest.objects.get(from_user=request.user,
                                                           to_user=request_user_profile.user)
                follow_request.delete()
                return Response({"status": "Follow Request Removed."}, status=status.HTTP_205_RESET_CONTENT)
            except:
                FollowRequest.objects.create(from_user=request.user,
                                             to_user=request_user_profile.user)
                return Response({"status": "Follow Request Sent to User"}, status=status.HTTP_201_CREATED)


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
            Profile.objects.get(user=follow_request.to_user).followers.add(
                follow_request.from_user)
            follow_request.delete()
            return Response({"status": "Follow Request Accepted."})
        elif confirmation.casefold() == "false":
            follow_request.delete()
            return Response({"status": "Follow Request Rejected."})
        else:
            return Response({"status": "Enter a valid confirmation."})


class StoryView(generics.GenericAPIView,
                mixins.ListModelMixin,
                mixins.DestroyModelMixin,
                mixins.CreateModelMixin):
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
        return super().list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class HomeStoryView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
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


class TagSearchView(generics.ListAPIView):
    serializer_class = TagSearchSerializer

    def get_queryset(self):
        query = self.request.data.get("search")
        return Tag.objects.annotate(similarity=TrigramSimilarity('tag', query),).filter(similarity__gt=0.15).order_by('-similarity')


class GetPostFromTagView(generics.ListAPIView):
    serializer_class = PostViewSerializer

    def get_queryset(self):
        tag = self.request.data.get("tag")
        try:
            return Tag.objects.get(tag=tag).post.all()
        except:
            return list()


class ProfileSearchView(generics.ListAPIView):
    model = Profile
    serializer_class = ProfileSearchSerializer

    def get_queryset(self):
        query = self.request.data.get("search")
        return Profile.objects.annotate(similarity=TrigramSimilarity('username', query),).filter(similarity__gt=0.065).order_by('-similarity')
