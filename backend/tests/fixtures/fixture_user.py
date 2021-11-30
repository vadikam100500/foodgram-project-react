import pytest


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser', email='testsuperuser@fdgrm.fake',
        password='1234567', first_name='TestSuperuser',
        last_name='TestSuperuser'
    )


@pytest.fixture
def token_user_superuser(user_superuser):
    from rest_framework.authtoken.models import Token

    Token.objects.get_or_create(user=user_superuser)
    return Token.objects.get(user=user_superuser)


@pytest.fixture
def user_superuser_client(token_user_superuser):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_user_superuser.key)
    return client


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser', email='testuser@fdgrm.fake',
        password='1234567', first_name='user', last_name='user bio'
    )


@pytest.fixture
def token_user(user):
    from rest_framework.authtoken.models import Token

    Token.objects.create(user=user)
    return Token.objects.get(user=user)


@pytest.fixture
def user_client(token_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_user.key)
    return client
