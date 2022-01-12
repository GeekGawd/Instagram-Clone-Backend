from django.db import models
from django.db.models import fields
from rest_framework import serializers
from core.models import User
from chat.models import Conversation, Message

class MessageUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'name']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    sender = MessageUserSerializer()
    receiver = MessageUserSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['sender', 'receiver', 'last_message']

    def get_last_message(self, instance):
        message = instance.message_set.first()
        if message:
            return MessageSerializer(instance=message).data
        else:
            return None


class ConversationSerializer(serializers.ModelSerializer):
    sender = MessageUserSerializer()
    receiver = MessageUserSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['sender', 'receiver', 'message_set']