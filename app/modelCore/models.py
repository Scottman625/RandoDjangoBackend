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

    about_me = models.TextField(blank=True,null=True)

    

    image = models.CharField(max_length=100, blank=True, null=True)

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
    
    # imageUrl = models.CharField(max_length=100, blank=True, null=True)

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

    def get_likes_count(self):
        count = UserLike.objects.filter(liked_user=self).count()
        return count

    def age(self):
        if self.birth_date is None:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def constellation(self):
        if self.birth_date:
            month = self.birth_date.month
            day = self.birth_date.day
            if ((month == 1 and day >= 20) or (month == 2 and day <= 18)):
                return '水瓶座'
            elif ((month == 2 and day >= 19) or (month == 3 and day <= 20)):
                return '雙魚座'
            elif ((month == 3 and day >= 21) or (month == 4 and day <= 19)):
                return '牡羊座'
            elif ((month == 4 and day >= 20) or (month == 5 and day <= 20)):
                return '金牛座'
            elif ((month == 5 and day >= 21) or (month == 6 and day <= 20)):
                return '雙子座'
            elif ((month == 6 and day >= 21) or (month == 7 and day <= 22)):
                return '巨蟹座'
            elif ((month == 7 and day >= 23) or (month == 8 and day <= 22)):
                return '獅子座'
            elif ((month == 8 and day >= 23) or (month == 9 and day <= 22)):
                return '處女座'
            elif ((month == 9 and day >= 23) or (month == 10 and day <= 22)):
                return '天秤座'
            elif ((month == 10 and day >= 23) or (month == 11 and day <= 21)):
                return '天蠍座'
            elif ((month == 11 and day >= 22) or (month == 12 and day <= 21)):
                return '射手座'
            elif ((month == 12 and day >= 22) or (month == 1 and day <= 19)):
                return '摩羯座'
        else:
            return None


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
            if Match.objects.filter(user1=self.user, user2=self.liked_user).count() == 0:
                Match.objects.create(user1=self.user, user2=self.liked_user)

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatRoom(models.Model):
    update_at = models.DateTimeField(auto_now=False, blank = True, null=True) 

    def last_update_at(self):
        last_message = ChatroomMessage.objects.filter(chatroom=self).order_by('create_at').first()
        return last_message.create_at

class ChatroomUserShip(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='chatroom_usership',
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
    sender = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null=True
    )

    content = models.TextField(default='', blank = True, null=True)
    create_at = models.DateTimeField(auto_now=False, blank = True,null=True) 

    image = models.ImageField(upload_to=image_upload_handler, blank=True, null=True)
    is_read_by_other_side = models.BooleanField(default=False)

    def should_show_sendTime(self):
        last_message = ChatroomMessage.objects.filter(sender=self.sender,create_at__lt=self.create_at,chatroom=self.chatroom).exclude(id=self.id).last()
        # print(last_message)
        if not last_message or (self.create_at - last_message.create_at).total_seconds() / 60 > 10:
            return True
        else:
            return False
        
class UserImage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        null=True
    )

    image = models.ImageField(
        upload_to=image_upload_handler, blank=True, null=True)
    
    update_at = models.DateTimeField(auto_now=True, blank = True,null=True) 

    def save(self,*args, **kwargs):
        super(UserImage, self).save(*args, **kwargs)
        user = self.user
        user.image = UserImage.objects.filter(user=user).first().image.url
        user.save() 

class Interest(models.Model):
    interest = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.interest

class UserInterest(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        null=True
    )
    interest = models.ForeignKey(
        Interest,
        on_delete = models.CASCADE,
        null=True
    )