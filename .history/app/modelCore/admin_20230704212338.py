from django.contrib import admin
from .models import User, ChatRoom, ChatroomMessage, ChatroomUserShip
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'line_id')



@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'update_at', )

@admin.register(ChatroomMessage)
class ChatroomMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chatroom', )

@admin.register(ChatroomUserShip)
class ChatroomUserShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chatroom')
