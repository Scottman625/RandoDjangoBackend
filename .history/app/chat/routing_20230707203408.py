from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from api import consumers

websocket_urlpatterns = [
    path('ws/chatroom/<int:chatroom_id>/', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    # WebSocket chat handler
    'websocket': URLRouter(websocket_urlpatterns),
})