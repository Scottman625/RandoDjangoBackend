from django.conf import settings
from django.core.management.base import BaseCommand
from modelCore.fakeData import importCityCounty, seedData, importUser,importUserLike()

class Command(BaseCommand):

    def handle(self, *args, **options):
        # importCityCounty()
        # seedData()
        # importUser()
        importUserLike()