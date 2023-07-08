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
        print(matches)
        matches_without_messages = matches.annotate(msg_count=Count('messages')).filter(msg_count=0)
        # print(matches_without_messages)
        # matches_without_messages = matches.difference(matches_with_messages)
        # print(matches_without_messages)

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
        queryset = queryset.annotate(msg_count=Count('chatroom_messages')).filter(msg_count__gt=0)
        # print(queryset)

        for i in range(len(queryset)):
            other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i]).filter(~Q(user=self.request.user)).first().user
            queryset[i].other_side_image_url = other_side_user.imageUrl
            queryset[i].other_side_name = other_side_user.name
            queryset[i].other_side_age = other_side_user.age
            queryset[i].other_side_career = other_side_user.career
            queryset[i].other_side_user = other_side_user

            if ChatroomMessage.objects.filter(chatroom=queryset[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=queryset[i]).order_by('-id').first()
                queryset[i].last_message = last_message.content[0:15]
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=queryset[i],is_read_by_other_side=False).filter(~Q(user=user))
                queryset[i].unread_num = chat_rooms_not_read_messages.count()
                queryset[i].last_message_time = queryset[i].last_update_at

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        # chatroom_id = self.request.query_params.get('chatroom_id')
        chatroom = self.get_object()
        other_side_user = ChatroomUserShip.objects.filter(Q(chatroom=chatroom)&~Q(user=user)).first().user
        chatroom.other_side_user = other_side_user
        chatroom.other_side_age = other_side_user.age
        if ChatroomMessage.objects.filter(chatroom=chatroom).count() > 0:
            chatroom.last_message_time = chatroom.last_update_at
        serializer = serializers.ChatRoomSerializer(chatroom)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        other_side_user_phone = request.data.get('other_side_user_phone')
        other_side_user = User.objects.get(phone=other_side_user_phone)
        user1_chatrooms = ChatroomUserShip.objects.filter(user_id=user)
        user2_chatrooms = ChatroomUserShip.objects.filter(user_id=other_side_user)
        
        # 將兩組chatrooms的id列表取交集
        common_chatroom_ids = set(user1_chatrooms).intersection(set(user2_chatrooms))


        
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
            serializer = serializers.ChatRoomSerializer(chatroom)
            response_data = serializer.data
            response_data['other_side_image_url'] = other_side_user.imageUrl
            
            # 返回序列化后的数据
            return Response(response_data)
        else:
            chatroom = ChatRoom.objects.filter(id__in=common_chatroom_ids).first()
            chatroom.other_side_user = other_side_user
            serializer = serializers.ChatRoomSerializer(chatroom)
            response_data = serializer.data

            return Response(response_data)

# class getChatRoomViewSet(APIView):

#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self,request):
#         user = self.request.user
#         chatroom_id = self.request.query_params.get('chatroom_id')
#         chatroom = ChatRoom.objects.get(id=chatroom_id)
#         other_side_user = ChatroomUserShip.objects.filter(Q(chatroom=chatroom)&~Q(user=user)).first().user
#         chatroom.other_side_user = other_side_user
#         chatroom.other_side_age = other_side_user.age
#         serializer = serializers.ChatRoomSerializer(chatroom)

#         return Response(serializer.data)

#     def post(self,request):
#         current_user = self.request.user
#         user_phone = self.request.data.get('user_phone')


#         other_side_user = User.objects.get(phone=user_phone)
#         chatroom_set1 = set(ChatroomUserShip.objects.filter(user=current_user).values_list('chatroom'))
#         chatroom_set2 = set(ChatroomUserShip.objects.filter(user=other_side_user).values_list('chatroom'))

#         chatroom_set = chatroom_set1.intersection(chatroom_set2)

#         if not list(chatroom_set):
#             chatroom = ChatRoom()
#             chatroom.save()

#             chatroomuserShip = ChatroomUserShip()
#             chatroomuserShip.chatroom = chatroom
#             chatroomuserShip.user = current_user
#             chatroomuserShip.save()

#             chatroomuserShip = ChatroomUserShip()
#             chatroomuserShip.chatroom = chatroom
#             chatroomuserShip.user = other_side_user
#             chatroomuserShip.save()
#         else:
#             chatroom = ChatRoom.objects.get(id=list(chatroom_set)[0][0])

#         chatroom.other_side_user = other_side_user
#         serializer = serializers.ChatRoomSerializer(chatroom)
#         return Response(serializer.data)

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
            queryset = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('-create_at')
            print(queryset[0])
            print('a')
            #update is_read_by_other_side
            queryset.filter(~Q(user=user)).update(is_read_by_other_side=True)
            print('b')
            for i in range(len(queryset)):
                if queryset[i].user == user:

                    queryset[i].message_is_mine = True

                other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i].chatroom).filter(~Q(user=self.request.user)).first().user
                print('other_side_user',other_side_user)
                queryset[i].other_side_image_url = other_side_user.imageUrl
                queryset[i].other_side_phone = other_side_user.phone
                queryset[i].should_show_time = queryset[i].should_show_sendTime

                # if queryset[i].case != None:
                #     queryset[i].orders = Order.objects.filter(case=queryset[i].case)
                # if queryset[i].case != None and queryset[i].is_this_message_only_case:
                #     queryset[i].case_detail = queryset[i].case

            serializer = serializers.MessageSerializer(queryset, many=True)

            # 把聊天室中兩人發過的案子都撈出來
            # 如果其中一人接了對方其中一個案子, 即可發圖片
            is_send_image = False

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
            message.user = user
            

            
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

            message.should_show_time = message.should_show_sendTime

            serializer = serializers.MessageSerializer(message)

            room_group_name = f"chat_{serializer.data['chatroom']}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': serializer.data['content']
                }
            )
            return Response(serializer.data)
        else:
            return Response({'message': "have no authority"})