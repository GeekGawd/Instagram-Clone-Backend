from django.urls import path

from socialuser.views import CreatePostView, PostView, ProfileUpdateView, ProfileView

urlpatterns = [
    path('post/create/', CreatePostView.as_view(), name='postcreate'),
    path('post/', PostView.as_view(), name='post'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='post'),
    path('profile/update/<int:pk>/', ProfileUpdateView.as_view(), name='post'),
]
