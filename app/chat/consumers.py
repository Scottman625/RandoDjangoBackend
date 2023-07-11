from channels.generic.websocket import AsyncWebsocketConsumer
import json
from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match
from channels.db import database_sync_to_async
from channels.auth import get_user
from django.db.models import Q, Count
from .chat_services import get_unread_chatroom_message_count



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = await get_user(self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

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
        
        messages = ChatroomMessage.objects.filter(~Q(sender=user.id)&Q(chatroom=room)&Q(is_read_by_other_side=False))
        messages.update(is_read_by_other_side=True)

    async def disconnect(self, close_code):
        print('channel is disconnect')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        
        user = await get_user(self.scope)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                

            }
        )


    async def chat_message(self, event):
        messages = event['messages']
        
        await self.send(text_data=json.dumps({
            'messages': messages,

        }))


class ChatMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = await get_user(self.scope)
        self.group_name = 'chatroom_list'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive_json(self, content, **kwargs):

        # print('testtttttttttttttt')
        user = await get_user(self.scope)
        chatroom_message_count_list = get_unread_chatroom_message_count(user)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'unread_count',
                'unread_num_list': chatroom_message_count_list
                

            }
        )

    async def unread_count(self, event):
        # 这个方法将处理你在 group_send 中发送的消息
        unread_num_list = event['unread_num_list']

        # 向 WebSocket 客户端发送消息
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'unread_num_list': unread_num_list
        }))



    async def disconnect(self, close_code):
        print('channel is disconnect')
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

  