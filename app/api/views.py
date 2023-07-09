from tracemalloc import start
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import date ,timedelta
from django.db.models import Q
from django.db.models import Avg , Count ,Sum
from django.shortcuts import get_object_or_404
import datetime

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match
from api import serializers
from messageApp.tasks import *

channel_layer = get_channel_layer()
# Create your views here.

class MatchedNotChattedUsersView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # 假设您已经有了获取当前用户的方法
        current_user = self.request.user
        print('z')
        # 使用上述提到的查询逻辑获取匹配但未聊天的用户
        matches = Match.objects.filter(Q(user1=current_user) | Q(user2=current_user))
        print('matches: ',matches)
        matches_without_messages = matches.annotate(msg_count=Count('messages')).filter(msg_count=0)
        # print(matches_without_messages)
        # matches_without_messages = matches.difference(matches_with_messages)
        print('matches_without_messages: ',matches_without_messages)

        queryset = User.objects.filter(
            Q(matches1__in=matches_without_messages) | 
            Q(matches2__in=matches_without_messages)
        ).exclude(pk=current_user.pk)

        for i in range(len(queryset)):
                
                # if queryset[i].user1 == current_user:
                #     other_side_user = queryset[i].user2
                # else:
                #     other_side_user = queryset[i].user1
                # print('other_side_user',other_side_user)
                queryset[i].other_side_image_url = queryset[i].imageUrl
                queryset[i].other_side_phone = queryset[i].phone
                queryset[i].age = queryset[i].age()
                # queryset[i].other_side_career = queryset[i].career


        # 使用 serializer 将用户对象序列化
        serializer = serializers.UserSerializer(queryset, many=True)
        
        # 返回序列化后的数据
        return Response(serializer.data)
    

class ChatRoomViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin):
    queryset = ChatRoom.objects.all()
    serializer_class = serializers.ChatRoomSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        chatroom_ids = list(ChatroomUserShip.objects.filter(user=user).values_list('chatroom', flat=True))
        queryset = self.queryset.filter(id__in=chatroom_ids).order_by('-update_at')
        if self.request.query_params.get('is_chat') == 'no':
            pass
        else:
            queryset = queryset.annotate(msg_count=Count('chatroom_messages')).filter(msg_count__gt=0)

        for i in range(len(queryset)):
            
            other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i]).filter(~Q(user=self.request.user)).first().user
            if ChatroomMessage.objects.filter(chatroom=queryset[i],sender=other_side_user,is_read_by_other_side=False).count() != 0:
                queryset[i].unread_num = ChatroomMessage.objects.filter(chatroom=queryset[i],sender=other_side_user,is_read_by_other_side=False).count()
            queryset[i].other_side_image_url = other_side_user.imageUrl
            queryset[i].other_side_name = other_side_user.name
            queryset[i].other_side_age = other_side_user.age
            queryset[i].other_side_career = other_side_user.career
            queryset[i].other_side_user = other_side_user
            queryset[i].current_user = user

            if ChatroomMessage.objects.filter(chatroom=queryset[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=queryset[i]).order_by('-id').first()
                queryset[i].last_message = last_message.content[0:15]
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=queryset[i],is_read_by_other_side=False).filter(~Q(sender=user))
                queryset[i].unread_num = chat_rooms_not_read_messages.count()
                queryset[i].last_message_time = queryset[i].last_update_at

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        # chatroom_id = self.request.query_params.get('chatroom_id')
        chatroom = self.get_object()
        print(chatroom)
        other_side_user = ChatroomUserShip.objects.filter(Q(chatroom=chatroom)&~Q(user=user)).first().user
        chatroom.other_side_user = other_side_user
        chatroom.current_user = user
        chatroom.other_side_age = other_side_user.age
        if ChatroomMessage.objects.filter(chatroom=chatroom).count() > 0:
            chatroom.last_message_time = chatroom.last_update_at
        serializer = serializers.ChatRoomSerializer(chatroom)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        other_side_user_phone = request.data.get('other_side_user_phone')
        other_side_user = User.objects.get(phone=other_side_user_phone)
        user1_chatrooms = list(ChatroomUserShip.objects.filter(user_id=user).values_list('chatroom'))
        user2_chatrooms = list(ChatroomUserShip.objects.filter(user_id=other_side_user).values_list('chatroom'))
        user1_chatrooms_list = [item[0] for item in user1_chatrooms]
        user2_chatrooms_list = [item[0] for item in user2_chatrooms]

        print('user1_chatrooms: ',user1_chatrooms_list)

        print('user2_chatrooms: ',user2_chatrooms_list)
        
        # 將兩組chatrooms的id列表取交集
        common_chatroom_ids = list(set(user1_chatrooms_list).intersection(set(user2_chatrooms_list)))

        print('common_chatroom_ids: ',common_chatroom_ids)


        
        # 根據這些id從Chatroom model中獲取chatroom object
        if ChatroomUserShip.objects.filter(user=user,chatroom=ChatRoom.objects.filter(id__in=common_chatroom_ids).first()).count() == 0:
            chatroom = ChatRoom.objects.filter(id__in=common_chatroom_ids).first()
            chatroom = ChatRoom()
            chatroom.save()
            chatroomuserShip = ChatroomUserShip()
            chatroomuserShip.chatroom = chatroom
            chatroomuserShip.user = user
            chatroomuserShip.save()

            chatroomuserShip = ChatroomUserShip()
            chatroomuserShip.chatroom = chatroom
            chatroomuserShip.user = other_side_user
            chatroomuserShip.save()

            chatroom.other_side_user = other_side_user
            chatroom.current_user = user
            serializer = serializers.ChatRoomSerializer(chatroom)
            response_data = serializer.data
            response_data['other_side_image_url'] = other_side_user.imageUrl
            response_data['other_side_name'] = other_side_user.name
            
            # 返回序列化后的数据
            return Response(response_data)
        else:
            chatroom = ChatRoom.objects.filter(id__in=common_chatroom_ids).first()
            chatroom.other_side_user = other_side_user
            chatroom.current_user = user
            serializer = serializers.ChatRoomSerializer(chatroom)
            response_data = serializer.data

            return Response(response_data)


class MessageViewSet(APIView):
    # queryset = Message.objects.all()
    # serializer_class = serializers.MessageSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        chatroom_id= self.request.query_params.get('chatroom_id')
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        user_ids = list(ChatroomUserShip.objects.filter(chatroom=chatroom).values_list('user', flat=True))

        if user.id in user_ids:
            queryset = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('create_at')
            # print(queryset[0])
            # print('a')
            #update is_read_by_other_side
            queryset.filter(~Q(sender=user)).update(is_read_by_other_side=True)
            # print('b')
            for i in range(len(queryset)):
                if queryset[i].sender == user:
                    queryset[i].message_is_mine = True
                else:
                    queryset[i].is_read_by_other_side = True
                    queryset[i].save()
                other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i].chatroom).filter(~Q(user=self.request.user)).first().user
                queryset[i].other_side_image_url = other_side_user.imageUrl
                queryset[i].other_side_phone = other_side_user.phone
                queryset[i].should_show_time = queryset[i].should_show_sendTime

            serializer = serializers.MessageSerializer(queryset, many=True)

            return Response(serializer.data)
 
        return Response({'message': "have no authority"})

    # 上傳聊天室訊息 文字/圖片
    def post(self, request):
        user = self.request.user
        chatroom_id = self.request.query_params.get('chatroom_id')
        content = request.data.get('content')
        image = request.data.get('image')

        chatroom = ChatRoom.objects.get(id=chatroom_id)
        user_ids = list(ChatroomUserShip.objects.filter(chatroom=chatroom).values_list('user', flat=True))
        chatroom_users = User.objects.filter(id__in=user_ids)

        if user in chatroom_users:
            other_side_user = chatroom_users.exclude(phone=user.phone)[0]
            message = ChatroomMessage()
            message.chatroom = chatroom
            message.sender = user
            match = Match.objects.filter(Q(user1=user,user2=other_side_user)|Q(user1=other_side_user,user2=user)).first()
            message.match = match

            
            if content != None:
                message.content = content
                title = '新訊息'
                sendFCMMessage(other_side_user,title,content)
            
            # upload image
            if image != None:
                message.image = image
                title = '新訊息'
                content =  user.name + '傳送了一張新圖片'
                sendFCMMessage(other_side_user,title,content)
            message.save()
            chatroom.update_at = datetime.datetime.now()
            chatroom.save()

            messages = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('create_at')

            for i in range(len(messages)):

                messages[i].should_show_time = messages[i].should_show_sendTime
                messages[i].other_side_image_url = other_side_user.imageUrl
                messages[i].other_side_phone = other_side_user.phone
                if messages[i].sender == user:
                    messages[i].message_is_mine = True

            
            serializer = serializers.MessageSerializer(messages, many=True)
            # print('chatroom_name: ' + str(serializer.data[-1]['chatroom']))
            room_group_name = f"chat_{str(serializer.data[-1]['chatroom'])}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'messages': serializer.data,
    

                }
            )
            return Response(serializer.data)
        else:
            return Response({'message': "have no authority"})