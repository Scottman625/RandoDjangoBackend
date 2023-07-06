import csv
import os
import datetime
from datetime import date ,timedelta
from django.utils import timezone
import pytz
from pytz import tzinfo
from django.db.models import Avg ,Sum 


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