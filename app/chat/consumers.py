from channels.generic.websocket import AsyncWebsocketConsumer
import json
from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match
from channels.db import database_sync_to_async
from channels.auth import get_user

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = await get_user(self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print(user)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # Set messages as read here
        await self.mark_messages_as_read(user=user)
        
        

    @database_sync_to_async
    def mark_messages_as_read(self,user):
        room = ChatRoom.objects.get(id=self.room_name)
        messages = ChatroomMessage.objects.filter(chatroom=room, is_read_by_other_side=False).exclude(sender=user.id)
        messages.update(is_read_by_other_side=True)

    async def disconnect(self, close_code):
        print('channel is disconnect')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        messages = event['messages']



        await self.send(text_data=json.dumps({
            'messages': messages,

        }))
