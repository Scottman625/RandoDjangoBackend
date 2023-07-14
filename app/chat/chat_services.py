from django.db.models import Count, Q
from modelCore.models import ChatRoom, ChatroomMessage, Match, ChatroomUserShip

def get_unread_chatroom_message_count(user,is_sender,other_side_user):
    if is_sender == True:
        receiver = other_side_user
        
        chatroomList = list(ChatroomUserShip.objects.filter(user=receiver).values_list('chatroom__id',flat=True))
        # print('chatroomList: ',chatroomList)
        chatrooms = ChatRoom.objects.filter(Q(id__in=chatroomList)&Q(chatroom_messages__sender=user)& Q(chatroom_messages__is_read_by_other_side=False)).annotate(unread_nums=Count('chatroom_messages'))
        # print('chatrooms: ',chatrooms)
            
           
        
    
    else:
        receiver = user
        chatroomList = list(ChatroomUserShip.objects.filter(user=receiver).values_list('chatroom__id',flat=True))
        # print('chatroomList_receive_json: ',chatroomList)
        chatrooms = ChatRoom.objects.filter(Q(id__in=chatroomList)&~Q(chatroom_messages__sender=receiver)& Q(chatroom_messages__is_read_by_other_side=False)).annotate(unread_nums=Count('chatroom_messages'))
        # print('chatrooms: ',chatrooms)



    chatroom_message_count_list = []
    for chatroom in chatrooms:
        chatroom_message_count_list.append({
            'chatroom': chatroom.id,
            'unread_nums': chatroom.unread_nums
        })

    return chatroom_message_count_list

def get_chatroom_list(user):
    chatrooms_list = list(ChatroomUserShip.objects.filter(user=user).values_list('chatroom',flat=True))
    chatrooms = ChatRoom.objects.filter(id__in=chatrooms_list).annotate(msg_count=Count('chatroom_messages')).filter(msg_count__gt=0).order_by('-update_at')
    return chatrooms