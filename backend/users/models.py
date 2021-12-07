from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):

    def _create_user(self, username, email, password,
                     first_name, last_name, **extra_fields):
        req_fields = {
            username: 'Введите никнейм',
            email: 'Введите почтовый адрес',
            password: 'Введите пароль',
            first_name: 'Введите ваше имя',
            last_name: 'Введите фамилию'
        }
        for field, message in req_fields.items():
            if not field:
                raise ValueError(message)
        email = self.normalize_email(email)
        globalusermodel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = globalusermodel.normalize_username(username)
        user = self.model(
            username=username, email=email, first_name=first_name,
            last_name=last_name, **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password,
                    first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            username, email, password, first_name, last_name, **extra_fields
        )

    def create_superuser(self, username, email, password,
                         first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            username, email, password, first_name, last_name, **extra_fields
        )


class CustomUser(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), max_length=250, unique=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
