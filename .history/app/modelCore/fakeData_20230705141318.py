import csv
import os
import datetime
from datetime import date ,timedelta
from django.utils import timezone
import pytz
from pytz import tzinfo
from django.db.models import Avg ,Sum ,Q
from modelCore.models import User, ChatRoom, ChatroomMessage, ChatroomUserShip,Match, UserLike


def importCityCounty():
    pass
    # module_dir = os.path.dirname(__file__)  # get current directory
    # file_path = os.path.join(module_dir, 'county.csv')

    # file = open(file_path,encoding="utf-8")
    # reader = csv.reader(file, delimiter=',')
    # for index, row in enumerate(reader):
    #     if index != 0:
    #         if City.objects.filter(name=row[0]).count()==0:
    #             city = City()
    #             city.name = row[0]
    #             city.newebpay_cityname = row[6]
    #             city.nameE = row[5].split(', ')[1]
    #             city.save()
    #         else:
    #             city = City.objects.get(name=row[0])

    #         county_name = row[2].replace(row[0],'')
    #         if County.objects.filter(name=county_name).count()==0:
    #             county = County()
    #         else:
    #             county = County.objects.get(name=county_name)
    #         county.city = city
    #         county.name = county_name
    #         county.addressCode = row[1]
    #         county.save()
    #         print(city.name + " " + county.name)

def seedData():
    pass

def importUser():
    user = User()
    user.name = 'Hong'
    user.phone = '0915323131'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

    user = User()
    user.name = 'Fang'
    user.phone = '0900000001'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

    user = User()
    user.name = 'Hex'
    user.phone = '0900000002'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

    user = User()
    user.name = 'Hsin'
    user.phone = '0900000003'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

    user = User()
    user.name = 'Ken'
    user.phone = '0900000004'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

    user = User()
    user.name = 'Blake'
    user.phone = '0900000005'
    user.gender = 'M'
    user.search_gender = 'F'
    user.imageUrl = 'assets/images/Kinu.png'

    user.save()

def importUserLike():
    # userlike = UserLike()
    # userlike.user = User.objects.get(id=3)
    # userlike.liked_user = User.objects.get(id=10)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=3)
    # userlike.liked_user = User.objects.get(id=11)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=3)
    # userlike.liked_user = User.objects.get(id=12)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=10)
    # userlike.liked_user = User.objects.get(id=3)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=10)
    # userlike.liked_user = User.objects.get(id=4)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=10)
    # userlike.liked_user = User.objects.get(id=5)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=4)
    # userlike.liked_user = User.objects.get(id=10)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=4)
    # userlike.liked_user = User.objects.get(id=13)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=4)
    # userlike.liked_user = User.objects.get(id=15)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=13)
    # userlike.liked_user = User.objects.get(id=5)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=13)
    # userlike.liked_user = User.objects.get(id=7)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=5)
    # userlike.liked_user = User.objects.get(id=13)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=5)
    # userlike.liked_user = User.objects.get(id=15)
    # userlike.save()

    # userlike = UserLike()
    # userlike.user = User.objects.get(id=15)
    # userlike.liked_user = User.objects.get(id=4)
    # userlike.save()

    userlike = UserLike()
    userlike.user = User.objects.get(id=3)
    userlike.liked_user = User.objects.get(id=11)
    userlike.save()

    userlike = UserLike()
    userlike.user = User.objects.get(id=3)
    userlike.liked_user = User.objects.get(id=12)
    userlike.save()

    userlike = UserLike()
    userlike.user = User.objects.get(id=3)
    userlike.liked_user = User.objects.get(id=13)
    userlike.save()

    userlike = UserLike()
    userlike.user = User.objects.get(id=3)
    userlike.liked_user = User.objects.get(id=14)
    userlike.save()

    userlike = UserLike()
    userlike.user = User.objects.get(id=3)
    userlike.liked_user = User.objects.get(id=15)
    userlike.save()

def importchatRoom():

    for match in Match.objects.all():
        chatroom = ChatRoom()
        chatroom.save()

        chatroomuserShip = ChatroomUserShip()
        chatroomuserShip.chatroom = chatroom
        chatroomuserShip.user = match.user1
        chatroomuserShip.save()

        chatroomuserShip = ChatroomUserShip()
        chatroomuserShip.chatroom = chatroom
        chatroomuserShip.user = match.user2
        chatroomuserShip.save()

def importMessage():
    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=6)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hello!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=13)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = "What's your name?"
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=7)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hi!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=12)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '嗨！'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=8)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '在幹嘛？'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=9)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '照片好好看喔！'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=6)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hello!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    cchatroom = ChatRoom.objects.get(id=7)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '嗨嗨'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=8)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hello!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=9)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = "What's your name?"
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=10)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hi!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=11)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '嗨！'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=12)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '在幹嘛？'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=13)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '照片好好看喔！'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=14)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = 'Hello!'
    chatroomMessage.save()

    chatroomMessage = ChatroomMessage()
    chatroom = ChatRoom.objects.get(id=15)
    chatroomMessage.chatroom = chatroom
    user2_condition = ~Q(user=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition1 = Q(user1=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition2 = Q(user1=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    condition3 = Q(user2=ChatroomUserShip.objects.filter(chatroom=chatroom).first().user)
    condition4 = Q(user2=ChatroomUserShip.objects.filter(user2_condition,chatroom=chatroom).first().user)
    chatroomMessage.match = Match.objects.filter((condition1&condition4)|(condition2&condition3)).first()
    chatroomMessage.user = ChatroomUserShip.objects.filter(chatroom=chatroom).first().user
    chatroomMessage.content = '嗨嗨'
    chatroomMessage.save()