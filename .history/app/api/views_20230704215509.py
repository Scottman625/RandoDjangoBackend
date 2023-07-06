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




# Create your views here.

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

        for i in range(len(queryset)):
            other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i]).filter(~Q(user=self.request.user)).first().user
            queryset[i].other_side_image_url = other_side_user.image
            queryset[i].other_side_name = other_side_user.name
            # print(other_side_user.name)
            # print(ChatroomMessage.objects.all())
            
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

