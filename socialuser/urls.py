from django.urls import path
from socialuser.models import Comment

from socialuser.views import BookmarkView, CommentCreateView, CreatePostView, FollowRequestView, GetPostFromTagView, HomeProfilePictureView,\
     LikeView, HomePostView, NotificationView, ProfileSearchView, StoryView, TagSearchView,\
    UserProfileAPIView, FollowerCreateView, HomeStoryView, ProfilePostView, GetStoryView

urlpatterns = [
    path('post/create/', CreatePostView.as_view(), name='postcreate'),
    path('post/', HomePostView.as_view(), name='post'),
    # path('profile/', ProfileView.as_view(), name='post'),
    path('profile/post/', ProfilePostView.as_view(), name='post'),
    # path('profile/update/<int:pk>/', ProfileUpdateView.as_view(), name='post'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    path('profile/follow/', FollowerCreateView.as_view(), name='follow'),
    path('follow/', FollowRequestView.as_view(), name='follow-request'),
    path('home/story/', HomeStoryView.as_view(), name='home-story'),
    path('story/', StoryView.as_view(), name='story'),
    path('story/get/', GetStoryView.as_view(), name='story'),
    path('post/like/', LikeView.as_view(), name='story'),
    path('post/comment/', CommentCreateView.as_view(), name='story'),
    path('search/tag/', TagSearchView.as_view(), name='tag-search'),
    path('tag/', GetPostFromTagView.as_view(), name='tag'),
    path('search/profile/', ProfileSearchView.as_view(), name='profile-search'),
    path('profile/bookmark/', BookmarkView.as_view(), name='profile-search'),
    path('profile/notification/', NotificationView.as_view(), name='profile-noti'),
    path('home/profile-picture/', HomeProfilePictureView.as_view(), name='profile-noti'),
]
