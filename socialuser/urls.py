from django.urls import path

from socialuser.views import PostUpload

urlpatterns = [
    path('post/', PostUpload.as_view(), name='post')
]