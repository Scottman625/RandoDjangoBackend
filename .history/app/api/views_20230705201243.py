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

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike
from api import serializers
from messageApp.tasks import *





# Create your views here.

class MatchedNotChattedUsersView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # 假设您已经有了获取当前用户的方法
        current_user = self.request.user

        # 使用上述提到的查询逻辑获取匹配但未聊天的用户
        matches = Match.objects.filter(Q(user1=current_user) | Q(user2=current_user))
        print(matches)
        matches_without_messages = matches.annotate(msg_count=Count('messages')).filter(msg_count=0)
        print(matches_without_messages)
        # matches_without_messages = matches.difference(matches_with_messages)
        # print(matches_without_messages)

        users_matched_but_not_chatted = User.objects.filter(
            Q(matches1__in=matches_without_messages) | 
            Q(matches2__in=matches_without_messages)
        ).exclude(pk=current_user.pk)
        print(users_matched_but_not_chatted)

        # 使用 serializer 将用户对象序列化
        serializer = serializers.UserSerializer(users_matched_but_not_chatted, many=True)
        
        # 返回序列化后的数据
        return Response(serializer.data)
    
    


class ChatRoomViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    queryset = ChatRoom.objects.all()
    serializer_class = serializers.ChatRoomSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        chatroom_ids = list(ChatroomUserShip.objects.filter(user=user).values_list('chatroom', flat=True))
        queryset = self.queryset.filter(id__in=chatroom_ids).order_by('-update_at')
        queryset = queryset.annotate(msg_count=Count('chatroom_messages')).filter(msg_count=0)
        print(queryset)

        for i in range(len(queryset)):
            other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i]).filter(~Q(user=self.request.user)).first().user
            queryset[i].other_side_image_url = other_side_user.imageUrl
            queryset[i].other_side_name = other_side_user.name
            # print(other_side_user.name)
            # print(ChatroomMessage.objects.all())
            if ChatroomMessage.objects.filter(chatroom=queryset[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=queryset[i]).order_by('-id').first()
                queryset[i].last_message = last_message.content[0:15]
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=queryset[i],is_read_by_other_side=False).filter(~Q(user=user))
                queryset[i].unread_num = chat_rooms_not_read_messages.count()

        return queryset
    
    

    def create(self, request, *args, **kwargs):
        user = self.request.user
        users = request.data.get('users')
        users_list = [int(i) for i in users.split(',')]
        if user.id in users_list:
            chatroom = ChatRoom()
            chatroom.save()
            for user_id in users_list:
                chatroomusership = ChatroomUserShip()
                chatroomusership.user = User.objects.get(id=user_id)
                chatroomusership.chatroom = chatroom
                chatroomusership.save()
            return Response({'message': "Successfully create"})
        else:
            return Response({'message': "have no authority"})

class getChatRoomViewSet(APIView):

    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get(self,request):
        chatroom = ChatRoom.objects.all()

        serializer = serializers.MessageSerializer(chatroom)
        return Response(serializer.data)

    def post(self,request):
        current_user = self.request.user
        user_phone = self.request.data.get('user_phone')


        the_other_side_user = User.objects.get(phone=user_phone)
        chatroom_set1 = set(ChatroomUserShip.objects.filter(user=current_user).values_list('chatroom'))
        chatroom_set2 = set(ChatroomUserShip.objects.filter(user=the_other_side_user).values_list('chatroom'))

        chatroom_set = chatroom_set1.intersection(chatroom_set2)

        if not list(chatroom_set):
            chatroom = ChatRoom()
            chatroom.save()

            chatroomuserShip = ChatroomUserShip()
            chatroomuserShip.chatroom = chatroom
            chatroomuserShip.user = current_user
            chatroomuserShip.save()

            chatroomuserShip = ChatroomUserShip()
            chatroomuserShip.chatroom = chatroom
            chatroomuserShip.user = the_other_side_user
            chatroomuserShip.save()
        else:
            chatroom = ChatRoom.objects.get(id=list(chatroom_set)[0][0])

        serializer = serializers.ChatRoomSerializer(chatroom)
        return Response(serializer.data)

class MessageViewSet(APIView):
    # queryset = Message.objects.all()
    # serializer_class = serializers.MessageSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        chatroom= self.request.query_params.get('chatroom')
        user_ids = list(ChatroomUserShip.objects.filter(chatroom=chatroom).values_list('user', flat=True))
  
        if user.id in user_ids:
            queryset = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('id')

            #update is_read_by_other_side
            queryset.filter(~Q(user=user)).update(is_read_by_other_side=True)

            for i in range(len(queryset)):
                if queryset[i].user == user:
                    queryset[i].message_is_mine = True
                    other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i].chatroom).filter(~Q(user=self.request.user)).first().user
                    queryset[i].other_side_image_url = other_side_user.imageUrl
                    queryset[i].other_side_name = other_side_user.name
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
        chatroom_id = self.request.query_params.get('chatroom')
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
            serializer = serializers.MessageSerializer(message)
            return Response(serializer.data)
        else:
            return Response({'message': "have no authority"})