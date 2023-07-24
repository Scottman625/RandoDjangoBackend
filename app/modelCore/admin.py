from django.contrib import admin
from .models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike, UserImage
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'line_id')

@admin.register(UserLike)
class UserLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'update_at', 'user', 'liked_user',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at','user1','user2' )

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'update_at', )

@admin.register(ChatroomMessage)
class ChatroomMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'chatroom','create_at' )

@admin.register(ChatroomUserShip)
class ChatroomUserShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chatroom')

@admin.register(UserImage)
class ChatroomUserShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image')
