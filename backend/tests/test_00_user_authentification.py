import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class Test00UserRegistrationAPI:
    url_login = '/api/auth/token/login/'
    url_logout = '/api/auth/token/logout/'
    wrong_data_answer = {
        "non_field_errors": [
            "Невозможно войти с предоставленными учетными данными."
        ]
    }

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_and_invaliddata_login(self, client):
        response = client.post(self.url_login)
        assert response.status_code != 404, (
            f'Страница `{self.url_login}` не найдена, '
            'проверь этот адрес в *urls.py*'
        )
        assert response.status_code == 400, (
            f'Проверь, что при POST запросе `{self.url_login}` без параметров '
            'не создается пользователь и возвращается статус 400'
        )
        assert response.json() == self.wrong_data_answer, (
            f'Проверь, что при POST запросе `{self.url_login}` без параметров '
            'в ответе есть сообщение о том, что вход не был осуществлен'
        )

        invalid_data = {
            'password': '!{=1',
            'email': 'invalid_email'
        }
        response = client.post(self.url_login, data=invalid_data)
        assert response.json() == self.wrong_data_answer, (
            f'Проверь, что при POST запросе `{self.url_login}` '
            'c не валидными параметрами, в ответе есть сообщение о том, '
            'что вход не был осуществлен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_01_valid_data_user_login(self, client, user_superuser,
                                      token_user_superuser):

        uncorrect_data = {
            'password': '!{=1',
            'email': 'testsuperuser@fdgrm.fake'
        }
        response = client.post(self.url_login, data=uncorrect_data)
        assert response.json() == self.wrong_data_answer, (
            f'Проверь, что при POST запросе `{self.url_login}` '
            'c не правильными данными, в ответе есть сообщение о том, '
            'что вход не был осуществлен'
        )

        user_superuser
        correct_data = {
            'password': '1234567',
            'email': 'testsuperuser@fdgrm.fake'
        }
        response = client.post(self.url_login, data=correct_data)
        assert response.status_code == 201, (
            f'Проверь, что при POST запросе `{self.url_login}` с валидными '
            'данными создается пользователь и возвращается статус 201'
        )
        assert response.json()["auth_token"] == token_user_superuser.key, (
            f'Проверь, что при POST запросе `{self.url_login}` с правильными '
            'данными в ответе выводится корректный токен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_not_auth_logout(self, client):
        response = client.post(self.url_logout)
        assert response.status_code == 401, (
            f'Проверь, что при POST запросе `{self.url_logout}` не '
            'авторизованного пользователя возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_logined_user_logout(self, user, user_client):
        from rest_framework.authtoken.models import Token

        response = user_client.post(self.url_logout)
        assert response.status_code == 204, (
            f'Проверь, что при POST запросе `{self.url_logout}` '
            'авторизованного пользователя возвращается статус 201'
        )
        assert not Token.objects.filter(user=user).exists(), (
            f'Проверь, что при POST запросе `{self.url_logout}` '
            'авторизованного пользователя, токен удаляется'
        )
