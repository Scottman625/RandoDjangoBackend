from django.urls import path, include
from user import views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'user'


urlpatterns = [
    path('get_user/', views.GetUserDataView.as_view(), name='get_user'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('login/', obtain_auth_token),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('update_line_id/', views.UpdateUserLineIdView.as_view()),
    path('update_user_password', views.UpdateUserPassword.as_view()),
    path('update_ATM_info', views.UpdateATMInfo.as_view()),
    path('update_user_background_image', views.UpdateUserBackgroundImage.as_view()),
    path('upload_user_images', views.UploadUserImage.as_view()),
    path('update_user_images/<int:pk>/', views.UpdateUserImage.as_view()),
    path('get_update_user_fcm_notify', views.GetUpdateUserFCMNotify.as_view()),
    path('deleteuser/<int:pk>/', views.DeleteUser.as_view()),
]
