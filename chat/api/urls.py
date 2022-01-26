from django.urls import path, re_path

from .views import *

urlpatterns = [
    # path('', ChatListView.as_view()),
    # path('create/<int:pk>', ChatDetailView.as_view())
    path('start/', ConversationCreateView.as_view(), name='start_convo'),
    re_path(r'chat/(?P<convo_id>[\w-]+)/', get_conversation, name='get_conversation'),
    path('profiles/', ConversationView.as_view(), name='list_conversation')
    # path('', views.conversations, name='conversations')
]