from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views


router = DefaultRouter()
router.register('chatroom', views.ChatRoomViewSet)

# router.register('login', views.Login)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),

]