from channels.db import database_sync_to_async
from rest_framework import serializers, status
from rest_framework.views import APIView
from django.db.models import Q
from chat.models import Conversation, Message
from core.models import User
from socialuser.models import Post, Profile
from .serializers import ConversationSerializer, ConversationListSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse
from socialuser.models import FollowRequest
from django.shortcuts import redirect


class ConversationCreateView(APIView):
    serializer_class = ConversationSerializer

    def get(self, request):
        convo_id = request.data.get("conversation_id")
        conversation = Conversation.objects.filter(id=convo_id)
        if not conversation.exists():
            return Response({'message': 'Conversation does not exist'})
        else:
            serializer = self.serializer_class(instance=conversation[0])
            return Response(serializer.data)

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        try:
            participant = User.objects.get(id=user_id)
            request_user_profile = Profile.objects.get(user=participant)
            session_user_profile = request.user.profile
        except:
            return Response({'message': 'You cannot chat with a non existent user'}, status=status.HTTP_404_NOT_FOUND)

        conversation = Conversation.objects.filter(Q(participant1=request.user, participant2=participant) | Q(
            participant1=participant, participant2=request.user))
        if conversation.exists():
            return redirect(reverse('get_conversation', args=(conversation[0].id,)))
        else:
            if Post.objects.post_authorization(request_user_profile, session_user_profile):
                conversation = Conversation.objects.create(
                participant1=request.user, participant2=participant)
                return Response(self.serializer_class(instance=conversation).data)
            try:
                FollowRequest.objects.get(from_user=request.user,
                                                            to_user=participant)
                return Response({"status": "Wait for follow request to be accepted."})
            except:
                FollowRequest.objects.create(from_user=request.user,
                                            to_user=participant)
                return Response({"status": "Follow Request Sent to User"})

@api_view(['GET'])
def get_conversation(request, convo_id):
    str = sorted(convo_id.split('-'))
    userid1, userid2 = str[0], str[1]
    conversation = Conversation.objects.filter(Q(participant1=userid1, participant2=userid2) | Q(
            participant1=userid2, participant2=userid1))
    if not conversation.exists():
        return Response({'message': 'Conversation does not exist'})
    else:
        serializer = ConversationSerializer(instance=conversation[0])
        return Response(serializer.data)


class ConversationView(APIView):
    serializer_class = ConversationListSerializer

    def conversations(self, request):
        conversation_list = Conversation.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user))
        serializer = self.serializer_class(
            instance=conversation_list, many=True)
        return Response(serializer.data)