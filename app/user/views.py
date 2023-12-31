from modelCore.models import User ,UserImage
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import viewsets, mixins

from user.serializers import UserSerializer, AuthTokenSerializer, UpdateUserSerializer ,GetUserSerializer
from api import serializers
from django.db.models import Q
from api.views import generate_presigned_url

class GetUserDataView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        # if self.request.user.line_id != None and self.request.user.line_id != '':
        #     self.request.user.is_gotten_line_id = True
        user = self.request.user
        user.total_likes_count = user.get_likes_count()
        user.image = generate_presigned_url(request=self.request,file_name=user.image)
        userImages = UserImage.objects.filter(user=user)
        for userImage in userImages:
            userImage.imageUrl = generate_presigned_url(request=self.request,file_name=userImage.image.name)
        user.userImages = userImages
        user.age = user.age()

        return user 

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

    def perform_create(self, serializer,):
        user = serializer.save(user=self.request.user)
        return user

#http://localhost:8000/api/user/token/  要用 post, 並帶參數
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

#http://localhost:8000/api/user/me/  要有 token
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UpdateUserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        # if self.request.user.line_id != None and self.request.user.line_id != '':
        #     self.request.user.is_gotten_line_id = True
        user = self.request.user
        user.total_likes_count = user.get_likes_count()
        userImages = UserImage.objects.filter(user=user)
        for userImage in userImages:
            userImage.imageUrl = generate_presigned_url(request=self.request,file_name=userImage.image.name)
        user.userImages = userImages

        return self.request.user

class UpdateUserLineIdView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    def put(self, request, format=None):
        try:
            # print(self.request.user)
            # print(self.request.data.get('line_id'))
            user = self.request.user
            user.line_id = self.request.data.get('line_id')
            user.save()
            return Response({'message': 'success update!'})
        except Exception as e:
            raise APIException("wrong token or null line_id")

class UpdateUserPassword(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    def put(self, request, format=None):
        user = self.request.user
        old_password = self.request.data.get('old_password')

        if user.check_password(old_password):
            new_password = self.request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({'message': 'success update!'})
        else:
            raise APIException("wrong old password")

class UpdateATMInfo(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, format=None):
        user = self.request.user
        user.ATMInfoBankCode = request.data.get('ATMInfoBankCode')
        user.ATMInfoBranchBankCode = request.data.get('ATMInfoBranchBankCode')
        user.ATMInfoAccount = request.data.get('ATMInfoAccount')
        user.save()
        serializer = GetUserSerializer(user)
        return Response(serializer.data)


class UpdateUserBackgroundImage(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, format=None):
        user = self.request.user

        background_image = request.data.get('background_image')
        if background_image != None:
            user.background_image = background_image
            
        user.save()
        serializer = GetUserSerializer(user)
        return Response(serializer.data)

class UploadUserImage(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        user = self.request.user
        image = request.FILES.get('image')
        UserImage.objects.create(user=user,image=image)
        userImages = UserImage.objects.filter(user=user)
        for userImage in userImages:
            userImage.imageUrl = generate_presigned_url(request=self.request,file_name=userImage.image.name)
        user.userImages = userImages
        serializer = GetUserSerializer(user)
        return Response(serializer.data)

class UpdateUserImage(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        user = self.request.user
        image = request.FILES.get('image')
        UserImage.objects.create(user=user,image=image)
        userImages = UserImage.objects.filter(user=user)
        for userImage in userImages:
            userImage.imageUrl = generate_presigned_url(request=self.request,file_name=userImage.image.name)
        user.userImages = userImages
        serializer = GetUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, format=None):
        user = self.request.user
        user.save()
        serializer = GetUserSerializer(user)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        user = self.request.user
        # userImageId = self.request.query_params.get('userImageId')
        UserImage.objects.get(user=user,id=pk).delete()
        userImages = UserImage.objects.filter(user=user)
        for userImage in userImages:
            userImage.imageUrl = generate_presigned_url(request=self.request,file_name=userImage.image.name)
        user.userImages = userImages
        serializer = GetUserSerializer(user)
        return Response(serializer.data)

class GetUpdateUserFCMNotify(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = self.request.user
        return Response({'is_fcm_notify':user.is_fcm_notify})

    def put(self, request, format=None):
        user = self.request.user
        is_fcm_notify = request.data.get('is_fcm_notify')
        if is_fcm_notify =='true' or is_fcm_notify =='True':
            user.is_fcm_notify = True
        else:
             user.is_fcm_notify = False
        user.save()
        return Response({'message':'ok'})

class DeleteUser(generics.DestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # lookup_field = 'pk'
    def delete(self, request, pk, format=None):
        
        auth_user = self.request.user
        user = User.objects.get(id=pk)
        if user == auth_user:
            if qualifications_to_delete_user(user) == False:
                return Response("continuous order exists")
            else:
                user.delete()
                return Response('delete user')
        else:
            return Response('not auth')

def qualifications_to_delete_user(user):
    for order in user.user_orders.all():
        if order.case.state == 'unComplete':
            return False
    for order in user.servant_orders.all():
        if order.case.state == 'unComplete':
            return False