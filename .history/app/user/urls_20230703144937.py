from django.urls import path, include
from user import views

app_name = 'user'


urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),

    path('update_line_id/', views.UpdateUserLineIdView.as_view()),
    path('update_user_password', views.UpdateUserPassword.as_view()),
    path('update_ATM_info', views.UpdateATMInfo.as_view()),

    path('update_user_background_image', views.UpdateUserBackgroundImage.as_view()),
    path('update_user_images', views.UpdateUserImage.as_view()),
    path('get_update_user_fcm_notify', views.GetUpdateUserFCMNotify.as_view()),

]
