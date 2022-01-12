from django.urls import path
from .views import *

urlpatterns = [
    # path('', ChatListView.as_view()),
    # path('create/<int:pk>', ChatDetailView.as_view())
    path('start/', ConversationCreateView.as_view(), name='start_convo'),
    # path('<int:convo_id>/', views.get_conversation, name='get_conversation'),
    # path('', views.conversations, name='conversations')
]