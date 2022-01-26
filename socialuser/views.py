import profile
from django.template import context
from core.models import User, Notification
from django.utils import timezone
from django.views.generic.list import ListView
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from socialuser.models import Bookmark, Comment, Profile, Post, FollowRequest, Story, Image, Video, Tag
from socialuser.serializers import BookmarkSerializer, CommentSerializer, FollowRequestSerializer, FollowRequestSerializer,\
    FollowerViewSerializer, HomeFeedStorySerializer,\
    LikePostSerializer, LikeSerializer, NotificationSerializer, PostSerializer, PostViewSerializer, ProfileSearchSerializer,\
    ProfileViewSerializer, StorySerializer, TagSearchSerializer, StoryViewSerializer
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import PageNumberPagination


# Create your views here.


# class CreatePostView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PostSerializer

#     def post(self, request):
#         photos = request.data['photos']
#         videos = request.data['videos']
#         caption = request.data.get("caption")

#         try:
#             request.data['user'] = request.user.id
#         except:
#             return Response({"status": "User not registered."}, status=status.HTTP_401_UNAUTHORIZED)

#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             post = serializer.save()

#         if photos is None and videos is None:
#             return Response({"status": "Cannot create post with no media."}, status=status.HTTP_406_NOT_ACCEPTABLE)

#         return Response({"status": "Post successfully created."}, status=status.HTTP_201_CREATED)

class CreatePostView(generics.CreateAPIView):
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        request.data.update({"user":request.user.id})
        if request.data.get("photos") or request.data.get("videos"):
            return super().post(request, *args, **kwargs)
        else:
            return Response({"status": "You cannot create a post with no media"}, status=status.HTTP_400_BAD_REQUEST)

class HomePostView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    model = Post
    serializer_class = PostViewSerializer

    def get_queryset(self):
        posts = []
        # print(dir(Post.objects.select_related("user")))
        print(Profile.objects.get(user=self.request.user).user.followers.all())
        print(self.request.user)
        for follower in Profile.objects.get_following(self.request):
            for post in Post.objects.filter(user=follower.user):
                posts.append(post)
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
        self.update(request, *args, **kwargs)
        return Response({"status": "Profile Updated Successfully."}, status=status.HTTP_200_OK)


class ProfilePostView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostViewSerializer

    def get_queryset(self):
        user_id = self.request.data.get("user_id")
        posts = Post.objects.filter(user=user_id)
        return posts

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"status": "Enter a user_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            request_user_profile = Profile.objects.get(
                user=User.objects.get(id=user_id))
            session_user_profile = Profile.objects.get(
                user=request.user)
        except:
            return Response({"status": "Request/Session User doesn't exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if Post.objects.post_authorization(request_user_profile, session_user_profile):
            return super().list(request, *args, **kwargs)
        return Response({"status": "Profile is Private"}, status=status.HTTP_403_FORBIDDEN)


class FollowerCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerViewSerializer

    def put(self, request):
        session_user_profile = Profile.objects.get(user=request.user)
        user_id = request.data.get("user_id")
        request_user_profile = Profile.objects.get(user=User.objects.get(id=user_id))

        if user_id == request.user.id:
            return Response({"status": "You cannot follow yourself."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if request_user_profile.followers.filter(id=request.user.id).exists():
            request_user_profile.followers.remove(request.user)
            data = {"follow": False, 
                    "no_of_following": request_user_profile.user.followers.count(),
                    "no_of_followers": request_user_profile.followers.count()}
            return Response(data, status=status.HTTP_208_ALREADY_REPORTED)

        elif not request_user_profile.is_private:
            request_user_profile.followers.add(request.user)
            data = {"follow": True, 
                    "no_of_following": request_user_profile.user.followers.count(),
                    "no_of_followers": request_user_profile.followers.count()}
            return Response(data, status=status.HTTP_200_OK)

        else:
            try:
                follow_request = FollowRequest.objects.get(from_user=request.user,
                                                           to_user=request_user_profile.user)
                follow_request.delete()
                data = {"follow": False, 
                        "no_of_following": request_user_profile.user.followers.count(),
                        "no_of_followers": request_user_profile.followers.count()}
                return Response(data, status=status.HTTP_206_PARTIAL_CONTENT)
            except:
                FollowRequest.objects.create(from_user=request.user,
                                             to_user=request_user_profile.user)
                data = {"follow": True, 
                        "no_of_following": request_user_profile.user.followers.count(),
                        "no_of_followers": request_user_profile.followers.count()}
                return Response(data, status=status.HTTP_201_CREATED)


class FollowRequestView(APIView):
    permission_classes = [IsAuthenticated]
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
            return Response({"status": "No Follow Request has been sent."}, status=status.HTTP_404_NOT_FOUND)

        if confirmation.casefold() == "true":
            Profile.objects.get(user=follow_request.to_user).followers.add(
                follow_request.from_user)
            follow_request.delete()
            return Response({"status": "Follow Request Accepted."}, status=status.HTTP_206_PARTIAL_CONTENT)
        elif confirmation.casefold() == "false":
            follow_request.delete()
            return Response({"status": "Follow Request Rejected."}, status=status.HTTP_226_IM_USED)
        else:
            return Response({"status": "Enter a valid confirmation."}, status=status.HTTP_406_NOT_ACCEPTABLE)


class StoryView(generics.GenericAPIView,
                mixins.CreateModelMixin,
                mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def post(self, request, *args, **kwargs):
        request.data.update({"user":request.user.id})
        if request.data.get("photos") or request.data.get("videos"):
            return super().create(request, *args, **kwargs)
        else:
            return Response({"status": "You cannot create a post with no media"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        story_id = request.data.get("story_id")   
        if story_id:
            try:
                Story.objects.get(id=story_id).delete()
                return Response({"status": "Story Deleted Successfully."}, status=status.HTTP_205_RESET_CONTENT)
            except ObjectDoesNotExist:
                return Response({"status": "Story does not exist"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"status": "Enter a story id."}, status=status.HTTP_400_BAD_REQUEST)
        


class HomeStoryView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeFeedStorySerializer

    def get_queryset(self):
        qs = Profile.objects.get(user=self.request.user.id).user.followers.all()
        stories = [profile for profile in qs if profile.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1)).exists()]
        
        if self.request.user.userstory.filter(created_at__gte = timezone.now() - timezone.timedelta(days=1)).exists():
            stories = [self.request.user.profile] + stories
            return stories
        else:
            return stories

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):

        post_id = request.data.get("post_id")
        comment_id = request.data.get("comment_id")
        post = Post.objects.filter(id=post_id).first()
        comment = Comment.objects.filter(id=comment_id).first()

        if not post and not comment:
            return Response({"status": "Enter a post/comment id to like"}, status=status.HTTP_400_BAD_REQUEST)

        if post:
            try:
                post.liked_by.get(id=request.user.id)
                post.liked_by.remove(request.user)
                return Response({"Like": False,
                                "no_of_likes":post.liked_by.count()}, status=status.HTTP_202_ACCEPTED)
            except:
                post.liked_by.add(request.user)
                return Response({"Like": True,
                                "no_of_likes":post.liked_by.count()}, status=status.HTTP_201_CREATED)

        elif comment:
            try:
                comment.liked_by.get(id=request.user.id)
                comment.liked_by.remove(request.user)
                return Response({"Like": False,
                                "no_of_likes":comment.liked_by.count()}, status=status.HTTP_202_ACCEPTED)
            except:
                comment.liked_by.add(request.user)
                return Response({"Like": True,
                                "no_of_likes":comment.liked_by.count()}, status=status.HTTP_201_CREATED)


class CommentCreateView(generics.GenericAPIView, mixins.ListModelMixin,
                         mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment_id = self.request.data.get("comment_id")
        return Comment.objects.get(id=comment_id)
    
    def get_queryset(self):
        post_id = self.request.data.get("post")
        comments = Post.objects.get(id=post_id).postcomments.filter(parent=None)
        return comments
    
    def post(self, request, *args, **kwargs):
        try:
            post_id=request.data['post']
            Post.objects.get(id=post_id)
        except (KeyError,ObjectDoesNotExist) as error:
            return Response({"status": "Enter a valid post id to view comments."}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        request.data.update({"comment_by": request.user.id})
        return super().create(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TagSearchView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = TagSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.data.get("search")
        return Tag.objects.annotate(similarity=TrigramSimilarity('tag', query),).filter(similarity__gt=0.15).order_by('-similarity')
    
    def post(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class GetPostFromTagView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = PostViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tag = self.request.data.get("tag")
        try:
            qs = Tag.objects.get(tag=tag).post.all()
            session_profile = Profile.objects.get(user=self.request.user)
            posts = [post for post in qs if Post.objects.post_authorization(post.user.profile, session_profile)]
            return posts
        except:
            return list()
    
    def post(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProfileSearchView(generics.GenericAPIView, mixins.ListModelMixin):
    model = Profile
    serializer_class = ProfileSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.data.get("search")
        return Profile.objects.annotate(similarity=TrigramSimilarity('username', query),).filter(similarity__gt=0.065).order_by('-similarity')
    
    def post(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GetStoryView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = StoryViewSerializer

    def get_queryset(self):
        user_id = self.request.data.get("user_id")
        qs = Story.objects.filter(user=User.objects.get(id=user_id),
            created_at__gte = timezone.now() - timezone.timedelta(days=1)).order_by('-id')
        qs.update(is_seen=True)
        return qs

    def post(self, request, *args, **kwargs):
        try:
            user_id = self.request.data['user_id']
            request_user_profile = Profile.objects.get(user=user_id)
            session_user_profile = Profile.objects.get(user=self.request.user.id)
            if Post.objects.post_authorization(request_user_profile, session_user_profile):
                return super().list(request, *args, **kwargs)
            else:
                return Response({"status": "Profile is Private"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except KeyError:
            return Response({"Enter a user id to view story."}, status=status.HTTP_400_BAD_REQUEST)

class BookmarkView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = PostViewSerializer

    def get_queryset(self):
        bookmark, _ = Bookmark.objects.get_or_create(user=self.request.user)
        return bookmark.posts.all()

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def post(self, request):
        user = request.user
        post_id = request.data.get("post_id")
        try:
            post = Post.objects.get(id=post_id)
            bookmark, _ = Bookmark.objects.get_or_create(user=user)
        except ObjectDoesNotExist:
            return Response({"status": "No such Post Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            bookmark.posts.get(id=post_id)
            bookmark.posts.remove(post)
            return Response({"Bookmark": False}, status=status.HTTP_202_ACCEPTED)
            
        except ObjectDoesNotExist:
            bookmark.posts.add(post)
            return Response({"Bookmark": True}, status=status.HTTP_200_OK)

# class LargeResultsSetPagination(PageNumberPagination):
#     page_size = 10

class NotificationView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    # pagination_class = LargeResultsSetPagination
    
    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        qs.update(is_seen=True)
        return qs
    
    def get_object(self):
        post_id = self.request.data.get("post_id")
        return Post.objects.get(id=post_id)
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        context = {"request": request}
        serializer = PostViewSerializer(instance, context=context)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class HomeProfilePictureView(APIView):
    def get(self, request):
        profile = request.user.profile
        return Response({"profile_picture": profile.profile_photo}, status=status.HTTP_200_OK)
    