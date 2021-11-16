import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        first_name = os.getenv('DJANGO_SUPERUSER_FIRST_NAME')
        last_name = os.getenv('DJANGO_SUPERUSER_LAST_NAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            User.objects.create_superuser(
                email=email, username=username, password=password,
                first_name=first_name, last_name=last_name
            )
        else:
            print('Admin account has already been initialized.')
