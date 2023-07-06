from rest_framework import serializers

from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike

class ChatRoomSerializer(serializers.ModelSerializer):
    other_side_image_url = serializers.CharField(default='')
    other_side_name = serializers.CharField(default='')
    last_message = serializers.CharField(default='')
    unread_num = serializers.IntegerField(default=0)

    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ('id',)