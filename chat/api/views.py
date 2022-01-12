from django.db.models import query
from rest_framework import serializers, status
from rest_framework.views import APIView
from django.db.models import Q
from chat.models import Conversation, Message
from core.models import User
from socialuser.models import Profile
from .serializers import ConversationSerializer, ConversationListSerializer
from rest_framework.response import Response
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from socialuser.models import FollowRequest


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
            profile, _ = Profile.objects.get_or_create(user=participant)
        except:
            return Response({'message': 'You cannot chat with a non existent user'}, status=status.HTTP_404_NOT_FOUND)

        conversation = Conversation.objects.filter(Q(sender=request.user, receiver=participant) | Q(
            sender=participant, receiver=request.user))
        if conversation.exists():
            return Response()
        else:
            if profile.is_private:
                try:
                    follow_request = FollowRequest.objects.get(from_user=request.user,
                                                               to_user=participant)
                    return Response({"status": "Wait for follow request to be accepted."})
                except:
                    FollowRequest.objects.create(from_user=request.user,
                                                 to_user=participant)
                    return Response({"status": "Follow Request Sent to User"})

            conversation = Conversation.objects.create(
                sender=request.user, receiver=participant)
            return Response(self.serializer_class(instance=conversation).data)


class ConversationView(APIView):
    serializer_class = ConversationListSerializer

    def conversations(self, request):
        conversation_list = Conversation.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user))
        serializer = self.serializer_class(
            instance=conversation_list, many=True)
        return Response(serializer.data)
