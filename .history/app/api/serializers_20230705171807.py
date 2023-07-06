from rest_framework import serializers

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id',)


class ChatRoomSerializer(serializers.ModelSerializer):
    other_side_image_url = serializers.CharField(default='')
    other_side_name = serializers.CharField(default='')
    last_message = serializers.CharField(default='')
    unread_num = serializers.IntegerField(default=0)
    chatroom_id = serializers.IntegerField(default=0)

    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ('id',)

class MessageSerializer(serializers.ModelSerializer):
    message_is_mine = serializers.BooleanField(read_only=True,default=False)
    other_side_image_url = serializers.CharField(default='')
    other_side_name = serializers.CharField(default='')

    class Meta:
        model = ChatroomMessage
        fields = '__all__'
        read_only_fields = ('id','user','chatroom','is_this_message_only_case','is_read_by_other_side')