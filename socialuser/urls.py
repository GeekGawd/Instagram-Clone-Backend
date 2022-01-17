from django.urls import path
from socialuser.models import Comment

from socialuser.views import CommentCreateView, CreatePostView, FollowRequestView, GetPostFromTagView,\
     LikeView, PostView, ProfileSearchView,ProfileView, StoryView, TagSearchView,\
    UserProfileChangeAPIView, FollowerCreateView, HomeStoryView

urlpatterns = [
    path('post/create/', CreatePostView.as_view(), name='postcreate'),
    path('post/', PostView.as_view(), name='post'),
    path('profile/', ProfileView.as_view(), name='post'),
    # path('profile/update/<int:pk>/', ProfileUpdateView.as_view(), name='post'),
    path('profile/update/', UserProfileChangeAPIView.as_view(), name='profile'),
    path('profile/follow/', FollowerCreateView.as_view(), name='follow'),
    path('follow/', FollowRequestView.as_view(), name='follow-request'),
    path('home/story/', HomeStoryView.as_view(), name='home-story'),
    path('story/', StoryView.as_view(), name='story'),
    path('post/like/', LikeView.as_view(), name='story'),
    path('post/comment/', CommentCreateView.as_view(), name='story'),
    path('search/tag/', TagSearchView.as_view(), name='tag-search'),
    path('tag/', GetPostFromTagView.as_view(), name='tag'),
    path('search/profile/', ProfileSearchView.as_view(), name='profile-search'),
]
