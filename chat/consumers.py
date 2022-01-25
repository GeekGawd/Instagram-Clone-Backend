# # chat/consumers.py
# import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
# from django.contrib.auth import get_user_model
# from .models import Message
# User = get_user_model()

# class ChatConsumer(WebsocketConsumer):

#     def fetch_messages(self, data):
#         # messages = Message.last_10_messages()
#         # content = {
#         #     'command': 'messages',
#         #     'messages': self.messages_to_json(messages)
#         # }
#         # self.send_message(content)
#         print(data)
#         print("fetch message")

#     def new_message(self, data):
#         # author = data['from']
#         # author_user = User.objects.filter(username=author)[0]
#         # message = Message.objects.create(
#         #     author=author_user, 
#         #     content=data['message'])
#         # content = {
#         #     'command': 'new_message',
#         #     'message': self.message_to_json(message)
#         # }
#         # return self.send_chat_message(content)
#         print(data)
#         print("new message")

#     def messages_to_json(self, messages):
#         result = []
#         for message in messages:
#             result.append(self.message_to_json(message))
#         return result

#     def message_to_json(self, message):
#         return {
#             'author': message.author.username,
#             'content': message.content,
#             'timestamp': str(message.timestamp)
#         }

#     commands = {
#         'fetch_messages': fetch_messages,
#         'new_message': new_message
#     }

#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )

#     def receive(self, text_data):
#         data = json.loads(text_data)
#         self.commands[data['command']](self, data)
        

#     def send_chat_message(self, message):    
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message
#         }))

import json
from pyexpat.errors import messages
from django.db.models import Q
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from core.models import User
from .models import Message, Conversation
from chat.api.serializers import MessageSerializer
from channels.exceptions import DenyConnection



class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def fetch_messages(self, userid1, userid2):
        conversation = Conversation.objects.filter(Q(participant1=userid1, participant2=userid2) | Q(
            participant1=userid2, participant2=userid1)).last()
        messages = conversation.messages.all()
        messages.update(is_seen=True)
        serialized_messages = MessageSerializer(instance=messages, many=True).data
        message_dict = {"messages": []}
        for msg in serialized_messages:
            message_dict["messages"].append(dict(msg))
        return message_dict
    
    @database_sync_to_async
    def get_conversation(self, userid1, userid2):
        return Conversation.objects.filter(Q(participant1=userid1, participant2=userid2) | Q(
            participant1=userid2, participant2=userid1)).last()
    
    @database_sync_to_async
    def message_create_function(self,sender, attachment, message, conversation):
        if attachment:
            created_message = Message.objects.create(
                sender=sender,
                attachment=attachment,
                text=message,
                conversation_id=conversation,
            )
        else:
            created_message = Message.objects.create(
                sender=sender,
                text=message,
                conversation_id=conversation,
            )
        
        return created_message

    @database_sync_to_async
    def message_to_dict(self, created_message):
        return (dict(MessageSerializer(instance=created_message).data))

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = f"chat_{self.room_name}"
        str = sorted(self.room_name.split('-'))
        userid1, userid2 = str[0], str[1]
        self.room_group_name = f"chat-{userid1}-{userid2}"
        data = await self.fetch_messages(userid1,userid2)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        if not(self.scope['user'].id is int(userid1) or self.scope['user'].id is int(userid2)):
            raise DenyConnection()
        await self.accept()
        await self.send(text_data=json.dumps(data))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)
        # unpack the dictionary into the necessary parts
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment"),
        )
        str = sorted(self.room_name.split('-'))
        userid1, userid2 = int(str[0]), int(str[1])
        sender = self.scope["user"]
        conversation = await self.get_conversation(userid1, userid2)

        # Attachment
        created_message = await self.message_create_function(sender,attachment,message, conversation)

        # Send message to room group
        chat_type = {"type": "chat_message"}
        message_serializer = await self.message_to_dict(created_message)
        return_dict = {**chat_type, **message_serializer}

        if created_message.attachment is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender.email,
                    "attachment": created_message.attachment,
                    "time": str(created_message.timestamp),
                },
            )
        else:
           await self.channel_layer.group_send(
                self.room_group_name,
                return_dict,
            )

    # Receive message from room group
    async def chat_message(self, event):
        dict_to_be_sent = event.copy()
        dict_to_be_sent.pop("type")
        print(dict_to_be_sent)

        # Send message to WebSocket
        await self.send(
                text_data=json.dumps(
                    dict_to_be_sent
                )
            )