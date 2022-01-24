from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from core.models import User

User = get_user_model()

class Conversation(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="convo_starter")
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="convo_participant")
    start_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender', blank=True, null=True)
    text = models.CharField(max_length=200, blank=True, null=True)
    attachment = models.FileField(blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)