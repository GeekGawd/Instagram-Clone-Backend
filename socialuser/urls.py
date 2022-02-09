from django.urls import path

from socialuser.views import CreatePostView, HomePostView

urlpatterns = [
    path('post/create/', CreatePostView.as_view(), name='postcreate'),
    path('post/', HomePostView.as_view(), name='post')
]