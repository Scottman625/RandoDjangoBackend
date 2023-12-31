from django.contrib.auth import get_user_model, authenticate
from modelCore.models import User, UserImage
from rest_framework import serializers

class UserImageSerializer(serializers.ModelSerializer):
    imageUrl = serializers.CharField(default='')

    class Meta:
        model = UserImage
        fields = '__all__'
        read_only_fields = ('id',)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    # is_gotten_line_id = serializers.BooleanField(default=False)
    total_unread_num = serializers.IntegerField(read_only=True,default=0)
    total_likes_count = serializers.IntegerField(read_only=True,default=0)
    userImages = UserImageSerializer(read_only=True, many=True)
    age = serializers.IntegerField(read_only=True,default=0)

    class Meta:
        model = get_user_model()
        fields = ('__all__')
        # extra_kwargs = {
        #     'password': {'write_only': True, 'min_length': 5},
        #     'line_id': {'write_only': True},
        #     'apple_id': {'write_only': True},
        # }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    total_unread_num = serializers.IntegerField(read_only=True,default=0)
    total_likes_count = serializers.IntegerField(read_only=True,default=0)
    userImages = UserImageSerializer(read_only=True, many=True)
    age = serializers.IntegerField(read_only=True,default=0)

    class Meta:
        model = get_user_model()
        fields = '__all__'
        read_only_fields = ('id',)

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    phone = serializers.CharField(allow_null=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        allow_null=True,
    )
    line_id = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        allow_null=True,
        required=False,
    )
    apple_id = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        allow_null=True,
        required=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        phone = attrs.get('phone')
        password = attrs.get('password')
        line_id = attrs.get('line_id')
        apple_id = attrs.get('apple_id')
        
        user = None

        if password and password != '00000':
            user = authenticate(
                request=self.context.get('request'),
                username=phone,
                password=password
            )
        
        if (line_id and line_id != ''):
            try:
                user = User.objects.get(line_id=line_id)
            except Exception as e:
                print('')
        
        if (apple_id and apple_id != ''):
            try:
                user = User.objects.get(apple_id=apple_id)
            except Exception as e:
                print('')

        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs

class GetUserSerializer(serializers.ModelSerializer):
    userImages = UserImageSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id',)

