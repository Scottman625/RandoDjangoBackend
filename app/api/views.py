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
from django.http import JsonResponse
import boto3
import os
from decouple import config
from botocore.exceptions import NoCredentialsError

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike
from api import serializers
from chat.chat_services import get_unread_chatroom_message_count, get_chatroom_list


channel_layer = get_channel_layer()
# Create your views here.

def generate_presigned_url(request,file_name):
    # 这是假设的文件名，实际情况中你可能需要从请求参数或数据库中获取
    # file_name = 'user_image.png' 
    # session = boto3.Session(
    # aws_access_key_id = config("AWS_ACCESS_KEY_ID"),
    # aws_secret_access_key = config("AWS_SECRET_ACCESS_KEY"),
    # )
    # 创建一个S3客户端
    s3_client = boto3.client('s3')
    
    file_name = file_name.replace('https://rando-app-bucket.s3.amazonaws.com/', '')
    file_name = file_name.split('?')[0]
    # print(file_name)
    try:
        # 生成预签名URL
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': "rando-app-bucket",
                                                            'Key': file_name},
                                                    ExpiresIn=3600)

    except NoCredentialsError:
        return JsonResponse({'error': 'No AWS credentials found'}, status=400)

    # print(response)
    # 返回生成的预签名URL
    return response

class UserPickedView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        current_user = self.request.user
        #先找出已經評價配對後的用戶ID列表，再篩選掉此列表中的用戶
        pickedUsersIdList = UserLike.objects.filter(user=current_user,is_like__isnull=False).values_list('liked_user',flat=True).distinct()
        notPickedYetUsers = User.objects.filter(~Q(id=current_user.id)&~Q(gender=current_user.gender)&~Q(id__in=pickedUsersIdList))
        print(notPickedYetUsers)

        for i in range(len(notPickedYetUsers)):

            notPickedYetUsers[i].image = generate_presigned_url(request=request,file_name=notPickedYetUsers[i].image)
            notPickedYetUsers[i].phone = notPickedYetUsers[i].phone
            notPickedYetUsers[i].age = notPickedYetUsers[i].age()

        serializer = serializers.UserSerializer(notPickedYetUsers, many=True)
        
        # 返回序列化后的数据
        return Response(serializer.data)
    
    def post(self, request, format=None):
        user = self.request.user
        liked_user_id = request.data.get('liked_user_id')
        other_side_user = User.objects.get(id=liked_user_id)
        print(other_side_user.phone)
        is_like = request.data.get('is_like')
        if is_like != None or is_like != '':
            if is_like == 'True' or is_like == 'true' or is_like == True:
                is_like = True
            else:
                is_like = False
        if UserLike.objects.filter(user=user,liked_user=other_side_user,is_like=is_like).count() == 0:
            UserLike.objects.create(user=user,liked_user=other_side_user,is_like=is_like)

        if Match.objects.filter(Q(user1=user,user2=other_side_user)|Q(user1=other_side_user,user2=user)).count() != 0:
            return Response({'result': "is matched"})
        else:
            return Response({'result': "not matched yet"})

class MatchedNotChattedUsersView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # 假设您已经有了获取当前用户的方法
        current_user = self.request.user
        # 使用上述提到的查询逻辑获取匹配但未聊天的用户
        matches = Match.objects.filter(Q(user1=current_user) | Q(user2=current_user))
        matches_without_messages = matches.annotate(msg_count=Count('messages')).filter(msg_count=0)
        # matches_without_messages = matches.difference(matches_with_messages)
        print(matches_without_messages)
        queryset = User.objects.filter(
            Q(matches1__in=matches_without_messages) | 
            Q(matches2__in=matches_without_messages)
        ).exclude(pk=current_user.pk).distinct()
        print(queryset)
        for i in range(len(queryset)):

            queryset[i].image = generate_presigned_url(request=request,file_name=queryset[i].image)
            queryset[i].other_side_phone = queryset[i].phone
            queryset[i].age = queryset[i].age()
            # queryset[i].imageUrl = generate_presigned_url(request=request,file_name=current_user.image)

                # queryset[i].other_side_career = queryset[i].career


        # 使用 serializer 将用户对象序列化
        serializer = serializers.UserSerializer(queryset, many=True)
        
        # 返回序列化后的数据
        return Response(serializer.data)
    

class RefreshChatMessageViewSet(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user = self.request.user.id
        chatroom_id = self.request.query_params.get('chatroom_id')
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        chatrooms = get_chatroom_list(user=user)
        messages = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('create_at')
        messages.filter(~Q(sender=user)).update(is_read_by_other_side=True)
        for each_chatroom in chatrooms:
                print(each_chatroom)
                other_side_user_chatroomUser = ChatroomUserShip.objects.filter(chatroom=each_chatroom).filter(~Q(user=user)).first().user
                if ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count() != 0:
                    each_chatroom.unread_nums = ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count()
                each_chatroom.other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user_chatroomUser.image)
                each_chatroom.other_side_name = other_side_user_chatroomUser.name
                if ChatroomMessage.objects.filter(chatroom=each_chatroom).count() > 0:
                    last_message = ChatroomMessage.objects.filter(chatroom=each_chatroom).order_by('-create_at').first()
                    each_chatroom.last_message_time = last_message.create_at
                    each_chatroom.update_at = last_message.create_at

                    if (last_message.content != '') and (last_message.content != None) :
                        each_chatroom.last_message = last_message.content[0:15]
                    elif (last_message.image != '' ) and (last_message.image != None):
                        each_chatroom.last_message = '已傳送圖片'
                    else:
                        each_chatroom.last_message = ''
                each_chatroom.chatroom_id = each_chatroom.id
                each_chatroom.other_side_age = other_side_user_chatroomUser.age
                each_chatroom.other_side_career = other_side_user_chatroomUser.career
                each_chatroom.current_user_id = user
                each_chatroom.other_side_user = other_side_user_chatroomUser
                each_chatroom.save()
        chatRoom_serializer = serializers.ChatRoomSerializer(chatrooms,many=True)

        user_ids = list(ChatroomUserShip.objects.filter(chatroom=chatroom).values_list('user', flat=True))
        chatroom_users = User.objects.filter(id__in=user_ids)

        if User.objects.get(id=user) in chatroom_users:
            other_side_user = chatroom_users.exclude(id=user)[0]

        for i in range(len(messages)):

                messages[i].should_show_time = messages[i].should_show_sendTime
                messages[i].other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user.image)
                messages[i].other_side_phone = other_side_user.phone
                if messages[i].sender == user:
                    messages[i].message_is_mine = True

        chatMessages_serializer = serializers.MessageSerializer(messages,many=True)
        room_group_name = f"chatRoomMessages_{str(user)}"
        async_to_sync(channel_layer.group_send)(
            room_group_name,  # 這裡需要替換成你的 group 名稱
            {
                'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                'chatrooms': chatRoom_serializer.data,
                'messages': chatMessages_serializer.data,
            }
        )

        print('data has refresh')
        return Response({'message': "ok"})
    
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
                queryset[i].unread_nums = ChatroomMessage.objects.filter(chatroom=queryset[i],sender=other_side_user,is_read_by_other_side=False).count()
            queryset[i].other_side_image_url = generate_presigned_url(request=self.request,file_name=other_side_user.image)
            queryset[i].other_side_name = other_side_user.name
            queryset[i].other_side_age = other_side_user.age
            queryset[i].other_side_career = other_side_user.career
            queryset[i].other_side_user = other_side_user
            queryset[i].current_user = user
            queryset[i].current_user_id = user.id
            queryset[i].current_user.imageUrl = generate_presigned_url(request=self.request,file_name=user.image)

            if ChatroomMessage.objects.filter(chatroom=queryset[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=queryset[i]).order_by('-id').first()
                if (last_message.content != '') and (last_message.content != None) :
                    queryset[i].last_message = last_message.content[0:15]
                elif (last_message.image != '' ) and (last_message.image != None):
                    queryset[i].last_message = '已傳送圖片'
                else:
                    queryset[i].last_message = ''
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=queryset[i],is_read_by_other_side=False).filter(~Q(sender=user))
                queryset[i].unread_nums = chat_rooms_not_read_messages.count()
                queryset[i].last_message_time = queryset[i].last_update_at
        

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        # chatroom_id = self.request.query_params.get('chatroom_id')
        chatroom = self.get_object()
        other_side_user = ChatroomUserShip.objects.filter(Q(chatroom=chatroom)&~Q(user=user)).first().user
        chatroom.other_side_user = other_side_user
        chatroom.current_user = user
        chatroom.other_side_age = other_side_user.age
        chatroom.current_user_id = user.id
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


        # 將兩組chatrooms的id列表取交集
        common_chatroom_ids = list(set(user1_chatrooms_list).intersection(set(user2_chatrooms_list)))


        
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
            

            if ChatroomMessage.objects.filter(chatroom=chatroom,sender=other_side_user,is_read_by_other_side=False).count() != 0:
                    chatroom.unread_nums = ChatroomMessage.objects.filter(chatroom=chatroom,sender=other_side_user,is_read_by_other_side=False).count()
            serializer = serializers.ChatRoomSerializer(chatroom)
            room_group_name = f"chatRoomMessages_{str(user.id)}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,  # 這裡需要替換成你的 group 名稱
                {
                    'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                    'chatrooms': serializer.data,
                    'messages': [],
                }
            )
            
            response_data = serializer.data
            response_data['other_side_image_url'] = generate_presigned_url(request=request,file_name=other_side_user.image)
            response_data['other_side_name'] = other_side_user.name
            response_data['other_side_image_url'] = generate_presigned_url(request=request,file_name=other_side_user.image)
            
            # 返回序列化后的数据
            return Response(response_data)
        else:
            chatroom = ChatRoom.objects.filter(id__in=common_chatroom_ids).first()
            chatroom.other_side_user = other_side_user
            chatroom.current_user = user
            chatroom.other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user.image)
            serializer = serializers.ChatRoomSerializer(chatroom)
            response_data = serializer.data

            return Response(response_data)
    
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        other_side_user_phone = request.data.get('other_side_user_phone')
        other_side_user = User.objects.get(phone=other_side_user_phone)
        print('other_side_user_id: ',other_side_user.id,'other_side_user_phone: ',other_side_user_phone)
        chatrooms_for_user1 = ChatroomUserShip.objects.filter(user=user).values_list('chatroom', flat=True)

        # 使用上一步的結果，找出user2也參與且是user1參與的chatroom
        common_chatrooms = ChatroomUserShip.objects.filter(user=other_side_user, chatroom__in=chatrooms_for_user1)

        # 如果需要得到待刪除的ChatRoom的實例列表
        chatroom_instance = [ship.chatroom for ship in common_chatrooms][0]
        chatroom_instance.delete()

        match = Match.objects.filter(Q(user1=user,user2=other_side_user)|Q(user1=other_side_user,user2=user)).first()
        match.delete()

        queryset = get_chatroom_list(user=user)

        if self.request.query_params.get('is_chat') == 'no':
            pass
        else:
            queryset = queryset.annotate(msg_count=Count('chatroom_messages')).filter(msg_count__gt=0)


        for i in range(len(queryset)):
            
            other_side_chatRoom_user = ChatroomUserShip.objects.filter(chatroom=queryset[i]).filter(~Q(user=self.request.user)).first().user
            print('other_side_chatRoom_user: ',other_side_chatRoom_user)
            if ChatroomMessage.objects.filter(chatroom=queryset[i],sender=other_side_chatRoom_user,is_read_by_other_side=False).count() != 0:
                queryset[i].unread_nums = ChatroomMessage.objects.filter(chatroom=queryset[i],sender=other_side_chatRoom_user,is_read_by_other_side=False).count()
            queryset[i].other_side_image_url = generate_presigned_url(request=self.request,file_name=other_side_chatRoom_user.image)
            queryset[i].other_side_name = other_side_chatRoom_user.name
            queryset[i].other_side_age = other_side_chatRoom_user.age
            queryset[i].other_side_career = other_side_chatRoom_user.career
            queryset[i].other_side_chatRoom_user = other_side_chatRoom_user
            queryset[i].current_user = user
            queryset[i].current_user_id = user.id
            queryset[i].current_user.imageUrl = generate_presigned_url(request=self.request,file_name=user.image)

            if ChatroomMessage.objects.filter(chatroom=queryset[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=queryset[i]).order_by('-id').first()
                if (last_message.content != '') and (last_message.content != None) :
                    queryset[i].last_message = last_message.content[0:15]
                elif (last_message.image != '' ) and (last_message.image != None):
                    queryset[i].last_message = '已傳送圖片'
                else:
                    queryset[i].last_message = ''
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=queryset[i],is_read_by_other_side=False).filter(~Q(sender=user))
                queryset[i].unread_nums = chat_rooms_not_read_messages.count()
                queryset[i].last_message_time = queryset[i].last_update_at


        serializer = serializers.ChatRoomSerializer(queryset, many=True)

        room_group_name = f"chatRoomMessages_{str(user.id)}"
        async_to_sync(channel_layer.group_send)(
            room_group_name,  # 這裡需要替換成你的 group 名稱
            {
                'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                'chatrooms': serializer.data,
                'messages': [],
            }
        )
        print(serializer.data)
       
        other_side_chatrooms = get_chatroom_list(user=other_side_user)

        other_side_chatrooms = other_side_chatrooms.annotate(msg_count=Count('chatroom_messages')).filter(msg_count__gt=0)

        for i in range(len(other_side_chatrooms)):
            
            other_side_chatroom_user = ChatroomUserShip.objects.filter(chatroom=other_side_chatrooms[i]).filter(~Q(user=other_side_user)).first().user
            if ChatroomMessage.objects.filter(chatroom=other_side_chatrooms[i],sender=other_side_user,is_read_by_other_side=False).count() != 0:
                other_side_chatrooms[i].unread_nums = ChatroomMessage.objects.filter(chatroom=other_side_chatrooms[i],sender=other_side_chatroom_user,is_read_by_other_side=False).count()
            other_side_chatrooms[i].other_side_image_url = generate_presigned_url(request=self.request,file_name=other_side_chatroom_user.image)
            other_side_chatrooms[i].other_side_name = other_side_chatroom_user.name
            other_side_chatrooms[i].other_side_age = other_side_chatroom_user.age
            other_side_chatrooms[i].other_side_career = other_side_chatroom_user.career
            other_side_chatrooms[i].other_side_user = other_side_chatroom_user
            other_side_chatrooms[i].current_user = other_side_user
            other_side_chatrooms[i].current_user_id = other_side_user.id
            other_side_chatrooms[i].current_user.imageUrl = generate_presigned_url(request=self.request,file_name=other_side_user.image)

            if ChatroomMessage.objects.filter(chatroom=other_side_chatrooms[i]).count() > 0:
                last_message = ChatroomMessage.objects.filter(chatroom=other_side_chatrooms[i]).order_by('-id').first()
                if (last_message.content != '') and (last_message.content != None) :
                    other_side_chatrooms[i].last_message = last_message.content[0:15]
                elif (last_message.image != '' ) and (last_message.image != None):
                    other_side_chatrooms[i].last_message = '已傳送圖片'
                else:
                    other_side_chatrooms[i].last_message = ''
            
                chat_rooms_not_read_messages = ChatroomMessage.objects.filter(chatroom=other_side_chatrooms[i],is_read_by_other_side=False).filter(~Q(sender=user))
                other_side_chatrooms[i].unread_nums = chat_rooms_not_read_messages.count()
                other_side_chatrooms[i].last_message_time = other_side_chatrooms[i].last_update_at

        print('other_side_user_id: ',other_side_user.id)
        other_side_serializer = serializers.ChatRoomSerializer(other_side_chatrooms,many=True)
        other_side_room_group_name = f"chatRoomMessages_{str(other_side_user.id)}"
        async_to_sync(channel_layer.group_send)(
            other_side_room_group_name,  # 這裡需要替換成你的 group 名稱
            {
                'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                'chatrooms': other_side_serializer.data,
                'messages': [],
            }
        )

        return Response(serializer.data)
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

            #update is_read_by_other_side
            queryset.filter(~Q(sender=user)).update(is_read_by_other_side=True)

            for i in range(len(queryset)):
                if queryset[i].sender == user:
                    queryset[i].message_is_mine = True
                else:
                    queryset[i].is_read_by_other_side = True
                    queryset[i].save()
                other_side_user = ChatroomUserShip.objects.filter(chatroom=queryset[i].chatroom).filter(~Q(user=self.request.user)).first().user
                queryset[i].other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user.image)
                queryset[i].other_side_phone = other_side_user.phone
                queryset[i].should_show_time = queryset[i].should_show_sendTime
                # queryset[i].current_user.imageUrl = generate_presigned_url(request=request,file_name=user.image)
                if queryset[i].image.name is not None and queryset[i].image.name.strip() != '':
                    queryset[i].imageUrl = generate_presigned_url(request=request,file_name=queryset[i].image.name)

            serializer = serializers.MessageSerializer(queryset, many=True)

            return Response(serializer.data)
 
        return Response({'message': "have no authority"})

    # 上傳聊天室訊息 文字/圖片
    def post(self, request):
        user = self.request.user
        chatroom_id = self.request.query_params.get('chatroom_id')
        content = request.data.get('content')

        image = request.FILES.get('image')

        chatroom = ChatRoom.objects.get(id=chatroom_id)
        user_ids = list(ChatroomUserShip.objects.filter(chatroom=chatroom).values_list('user', flat=True))
        chatroom_users = User.objects.filter(id__in=user_ids)

        if user in chatroom_users:
            other_side_user = chatroom_users.exclude(phone=user.phone)[0]
            message = ChatroomMessage()
            message.create_at = datetime.datetime.now()
            message.chatroom = chatroom
            message.sender = user
            match = Match.objects.filter(Q(user1=user,user2=other_side_user)|Q(user1=other_side_user,user2=user)).first()
            message.match = match

            
            if content != None:
                message.content = content
                title = '新訊息'
                # sendFCMMessage(other_side_user,title,content)
            
            # upload image
            if image != None:
                message.image = image
                title = '新訊息'
                content =  user.name + '傳送了一張新圖片'
                # sendFCMMessage(other_side_user,title,content)
            message.save()
            chatroom.update_at = datetime.datetime.now()
            chatroom.save()

            messages = ChatroomMessage.objects.filter(chatroom=chatroom).order_by('create_at')

            for i in range(len(messages)):

                messages[i].should_show_time = messages[i].should_show_sendTime
                messages[i].other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user.image)
                messages[i].other_side_phone = other_side_user.phone
                if messages[i].sender == user:
                    messages[i].message_is_mine = True

            
            serializer = serializers.MessageSerializer(messages, many=True)

            chatrooms = get_chatroom_list(user=user)
            for each_chatroom in chatrooms:
                print(each_chatroom)
                other_side_user_chatroomUser = ChatroomUserShip.objects.filter(chatroom=each_chatroom).filter(~Q(user=user)).first().user
                if ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count() != 0:
                    each_chatroom.unread_nums = ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count()
                each_chatroom.other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user_chatroomUser.image) 
                each_chatroom.other_side_name = other_side_user_chatroomUser.name
                if ChatroomMessage.objects.filter(chatroom=each_chatroom).count() > 0:
                    last_message = ChatroomMessage.objects.filter(chatroom=each_chatroom).order_by('-create_at').first()
                    each_chatroom.last_message_time = last_message.create_at
                    each_chatroom.update_at = last_message.create_at

                    if (last_message.content != '') and (last_message.content != None) :
                        each_chatroom.last_message = last_message.content[0:15]
                    elif (last_message.image != '' ) and (last_message.image != None):
                        each_chatroom.last_message = '已傳送圖片'
                    else:
                        each_chatroom.last_message = ''
                each_chatroom.chatroom_id = each_chatroom.id
                each_chatroom.other_side_age = other_side_user_chatroomUser.age
                each_chatroom.other_side_career = other_side_user_chatroomUser.career
                each_chatroom.current_user_id = user.id
                each_chatroom.other_side_user = other_side_user_chatroomUser
                each_chatroom.save()
                
            chatRoom_serializer = serializers.ChatRoomSerializer(chatrooms,many=True)
            room_group_name = f"chatRoomMessages_{str(user.id)}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,  # 這裡需要替換成你的 group 名稱
                {
                    'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                    'chatrooms': chatRoom_serializer.data,
                    'messages': serializer.data,
                }
            )

            other_side_chatrooms = get_chatroom_list(user=other_side_user)
            for each_chatroom in other_side_chatrooms:
                # print(each_chatroom)
                other_side_user_chatroomUser = ChatroomUserShip.objects.filter(chatroom=each_chatroom).filter(~Q(user=other_side_user)).first().user
                if ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count() != 0:
                    each_chatroom.unread_nums = ChatroomMessage.objects.filter(chatroom=each_chatroom,sender=other_side_user_chatroomUser,is_read_by_other_side=False).count()
                each_chatroom.other_side_image_url = generate_presigned_url(request=request,file_name=other_side_user_chatroomUser.image) 
                each_chatroom.other_side_name = other_side_user_chatroomUser.name
                if ChatroomMessage.objects.filter(chatroom=each_chatroom).count() > 0:
                    last_message = ChatroomMessage.objects.filter(chatroom=each_chatroom).order_by('-create_at').first()
                    each_chatroom.last_message_time = last_message.create_at
                    each_chatroom.update_at = last_message.create_at

                    if (last_message.content != '') and (last_message.content != None) :
                        each_chatroom.last_message = last_message.content[0:15]
                    elif (last_message.image != '' ) and (last_message.image != None):
                        each_chatroom.last_message = '已傳送圖片'
                    else:
                        each_chatroom.last_message = ''
                each_chatroom.chatroom_id = each_chatroom.id
                each_chatroom.other_side_age = other_side_user_chatroomUser.age
                each_chatroom.other_side_career = other_side_user_chatroomUser.career
                each_chatroom.current_user_id = other_side_user.id
                each_chatroom.other_side_user = other_side_user_chatroomUser
                each_chatroom.save()
                
            other_side_chatRoom_serializer = serializers.ChatRoomSerializer(other_side_chatrooms,many=True)

            other_side_room_group_name = f"chatRoomMessages_{str(other_side_user.id)}"
            async_to_sync(channel_layer.group_send)(
                other_side_room_group_name,  # 這裡需要替換成你的 group 名稱
                {
                    'type': 'chatrooms',  # 這裡需要替換成你在 consumer 中定義的方法名稱
                    'chatrooms': other_side_chatRoom_serializer.data,
                    'messages': serializer.data,
                }
            )

            return Response(serializer.data)
        else:
            return Response({'message': "have no authority"})