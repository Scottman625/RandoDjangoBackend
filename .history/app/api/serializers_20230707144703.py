from rest_framework import serializers

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike

class UserSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(default=None)
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id',)

# class MatchSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Match
#         fields = '__all__'
#         read_only_fields = ('id','other_side_age','other_side_career')

class ChatRoomSerializer(serializers.ModelSerializer):
    other_side_image_url = serializers.CharField(default='')
    other_side_name = serializers.CharField(default='')
    last_message = serializers.CharField(default='')
    unread_num = serializers.IntegerField(default=0)
    chatroom_id = serializers.IntegerField(default=0)
    update_at = serializers.DateTimeField(default=None)
    other_side_age = serializers.IntegerField(default=None)
    other_side_career = serializers.CharField(default='')
    other_side_user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ('id',)

class MessageSerializer(serializers.ModelSerializer):
    message_is_mine = serializers.BooleanField(read_only=True,default=False)
    other_side_image_url = serializers.CharField(default='')
    other_side_phone = serializers.CharField(default='')
    should_show_time = serializers.BooleanField(read_only=True,default=True)

    class Meta:
        model = ChatroomMessage
        fields = '__all__'
        read_only_fields = ('id','user','chatroom','is_this_message_only_case','is_read_by_other_side')