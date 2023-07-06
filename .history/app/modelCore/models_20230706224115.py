import pathlib
from unicodedata import category
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from datetime import date
from django.db.models import Avg, Sum
# from ckeditor_uploader.fields import RichTextUploadingField


def image_upload_handler(instance, filename):
    fpath = pathlib.Path(filename)
    new_fname = str(uuid.uuid1())  # uuid1 -> uuid + timestamp
    return f'images/{new_fname}{fpath.suffix}'


@property
def get_photo_url(self):
    if self.photo and hasattr(self.photo, 'url'):
        return self.photo.url
    else:
        return "/static/web/assets/img/generic/2.jpg"

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not phone:
            raise ValueError('Users must have an phone')
        # user = self.model(email=self.normalize_email(email), **extra_fields)
        user = self.model(
            phone=phone,
            name=extra_fields.get('name'),
            line_id=extra_fields.get('line_id'),
            apple_id=extra_fields.get('apple_id'),
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, password, **extra_fields):
        """Creates and saves a new super user"""
        user = self.create_user(phone, password, **extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=10, unique=True)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    name = models.CharField(max_length=255, null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)

    career = models.CharField(max_length=10, blank=True,null=True)

    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    SEARCH_GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('A', 'All'),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default=MALE)
    
    search_gender = models.CharField(
        max_length=1, choices=SEARCH_GENDER_CHOICES, default=FEMALE)

    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(
        upload_to=image_upload_handler, blank=True, null=True)
    
    imageUrl = models.CharField(max_length=100, blank=True, null=True)

    line_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True)
    apple_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True)

    background_image = models.ImageField(
        upload_to=image_upload_handler, blank=True, null=True)

    # ATMInfoBankCode = models.CharField(
    #     max_length=20, default='', blank=True, null=True)
    # ATMInfoBranchBankCode = models.CharField(
    #     max_length=20, default='', blank=True, null=True)
    # ATMInfoAccount = models.CharField(
    #     max_length=20, default='', blank=True, null=True)

    USERNAME_FIELD = 'phone'

    def age(self):
        if self.birth_date is None:
            print('none')
            return None
        today = date.today()
        print(today)
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class UserLike(models.Model):
    update_at = models.DateTimeField(auto_now=True, blank = True, null=True) 
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    liked_user = models.ForeignKey(
        User,
        related_name='liked_by',
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        # Call the original save method to save the UserLike instance
        super(UserLike, self).save(*args, **kwargs)
        
        # Check if a matching UserLike exists
        if UserLike.objects.filter(user=self.liked_user, liked_user=self.user).exists():
            # If it does, create a new Match instance
            Match.objects.create(user1=self.user, user2=self.liked_user)

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatRoom(models.Model):
    update_at = models.DateTimeField(auto_now=True, blank = True, null=True) 

class ChatroomUserShip(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
    ) 

    is_create = models.BooleanField(default=False)

class ChatroomMessage(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='chatroom_messages',
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="messages",null=True)

    # user is the one who make message
    user = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null=True
    )

    content = models.TextField(default='', blank = True, null=True)
    create_at = models.DateTimeField(auto_now=True, blank = True,null=True) 

    image = models.ImageField(upload_to=image_upload_handler, blank=True, null=True)
    is_read_by_other_side = models.BooleanField(default=False)

    def should_show_sendTime(self):
        last_message = ChatroomMessage.objects.filter(user=self.user,create_at__lt=self.create_at,chatroom=self.chatroom).exclude(id=self.id).last()
        print(last_message)
        if not last_message or (self.create_at - last_message.create_at).total_seconds() / 60 > 10:
            return True
        else:
            return False