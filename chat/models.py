from statistics import mode
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from core.models import User
from socialuser.models import Bookmark

User = get_user_model()

class Conversation(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="convo_starter")
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="convo_participant")
    start_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender', blank=True, null=True)
    text = models.CharField(max_length=200, blank=True, null=True)
    attachment = models.URLField(blank=True, null=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=True, null=True, related_name="messages")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ('-timestamp',)