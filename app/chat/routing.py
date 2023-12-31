from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path,re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chatRoomMessages/(?P<room_name>\w+)/$', consumers.ChatMessageConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    # WebSocket chat handler
    'websocket': URLRouter(websocket_urlpatterns),
})