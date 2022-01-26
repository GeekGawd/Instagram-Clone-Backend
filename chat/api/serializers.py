import profile
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from core.models import User
from chat.models import Conversation, Message

class MessageUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'profile_picture']

    def get_username(self, instance):
        return instance.profile.username

    def get_profile_picture(self, instance):
        return instance.profile.profile_photo

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('conversation_id',)


class ConversationListSerializer(serializers.ModelSerializer):
    participant1 = MessageUserSerializer()
    participant2 = MessageUserSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['participant1', 'participant2', 'last_message']

    def get_last_message(self, instance):
        message = instance.messages.first()
        if message:
            return MessageSerializer(instance=message).data
        else:
            return None
    
    def to_representation(self, instance):
        request=self.context.get('request')
        data=super().to_representation(instance)

        if request.user.id is instance.participant1.id:
            data.pop("participant1")
        else:
            data.pop("participant2")
        data['request_user'] = request.user.id
        return data


class ConversationSerializer(serializers.ModelSerializer):
    participant1 = MessageUserSerializer()
    participant2 = MessageUserSerializer()
    messages = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['participant1', 'participant2', 'messages']