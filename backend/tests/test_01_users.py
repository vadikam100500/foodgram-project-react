import pytest


class Test01UserAPI:
    url = '/api/users/'
    url_detail = '/api/users/1/'
    url_me = '/api/users/me/'
    url_pass = '/api/users/set_password/'

    def data_add_del(self, data, what, what_value, pop=None):
        check_data = []
        for user_data in data:
            user_data[what] = what_value
            if pop:
                user_data.pop(pop)
            check_data.append(user_data)
        return check_data

    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_auth_get(self, client, create_users):
        main_data = create_users
        check_data = self.data_add_del(main_data, 'is_subscribed',
                                       False, 'password')

        response = client.get(self.url)
        data = response.json()
        assert response.status_code != 404, (
            f'Страница `{self.url}` не найдена, проверь этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации возвращается статус 200'
        )
        assert type(data) == list, (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации '
            'возвращаемые данные в списке'
        )
        assert 'results' not in data, (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации '
            'возвращаете данные без  пагинации, если не указан '
            'параметр `limit`'
        )
        assert 'is_subscribed' in data[0], (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации  есть параметр is_subscribed'
        )
        assert check_data == data, (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации возвращаются корректные данные'
        )
        data = client.get(f'{self.url}?limit=2').json()
        for param in ('count', 'next', 'previous', 'results'):
            assert param in data, (
                'Проверь, что при GET запросе `{self.url}?limit=2` '
                'без токена авторизации '
                'возвращаете данные с пагинацией. '
                f'Не найден параметр `{param}`'
            )
        assert data['count'] == 10, (
            f'Проверь, что при GET запросе `{self.url}?limit=2` '
            'без токена авторизации '
            'возвращаете данные с пагинацией. '
            'Значение параметра `count` не правильное'
        )
        assert (
            len(data['results']) == 2
            and data['results'][0] == check_data[0]
            and data['results'][1] == check_data[1]
        ), (
            f'Проверь, что при GET запросе `{self.url}?limit=2` '
            'без токена авторизации '
            'возвращаете данные с пагинацией. '
            'Значение параметра `results` не правильное'
        )
        data = client.get(f'{self.url}?page=2&limit=2').json()
        assert (
            len(data['results']) == 2
            and data['results'][0] == check_data[2]
            and data['results'][1] == check_data[3]
        ), (
            f'Проверь, что при GET запросе `{self.url}?page=2&limit=2` '
            'без токена авторизации '
            'возвращаете корректные данные при указании номера страницы и '
            'лимита. Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_users_auth_user_get(self, user_client, create_users):
        from django.contrib.auth import get_user_model

        from interactions.models import Follow

        user = get_user_model()
        main_data = create_users
        check_data = self.data_add_del(main_data, 'is_subscribed',
                                       False, 'password')

        response = user_client.get(self.url)

        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токеном авторизации возвращается статус 200'
        )
        assert check_data == response.json()[:-1], (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токенoм авторизации возвращаются корректные данные'
        )

        user1 = user.objects.get(username='TestUser')
        user2 = user.objects.get(id=0)
        follow = Follow.objects.create(user=user1, author=user2)

        response = user_client.get(self.url)
        assert response.json()[0]['is_subscribed'] is True, (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токенoм авторизации отопоражается true '
            'если автор подписан'
        )

        follow.delete()

        data = user_client.get(f'{self.url}?page=2&limit=2').json()
        for param in ('count', 'next', 'previous', 'results'):
            assert param in data, (
                f'Проверь, что при GET запросе `{self.url}?page=2&limit=2` '
                'для авторизованного пользователя '
                'возвращаете данные с пагинацией. '
                f'Не найден параметр `{param}`'
            )
        assert (
            len(data['results']) == 2
            and data['results'][0] == check_data[2]
            and data['results'][1] == check_data[3]
        ), (
            'Проверьте, что при GET запросе `{self.url}?page=2&limit=2` '
            'возвращаете корректные данные при указании номeра страницы и '
            'лимита для авторизованного пользователя. '
            'Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_users_superuser_get(self, user_superuser_client, create_users):
        main_data = create_users
        check_data = self.data_add_del(main_data, 'is_subscribed',
                                       False, 'password')

        response = user_superuser_client.get(self.url)

        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токеном суперпользователя возвращается статус 200'
        )
        assert check_data == response.json()[:-1], (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токеном суперпользователя возвращаются корректные данные'
        )
        data = user_superuser_client.get(f'{self.url}?page=2&limit=2').json()
        for param in ('count', 'next', 'previous', 'results'):
            assert param in data, (
                f'Проверь, что при GET запросе `{self.url}?page=2&limit=2` '
                'для суперпользователя '
                'возвращаете данные с пагинацией. '
                f'Не найден параметр `{param}`'
            )
        assert (
            len(data['results']) == 2
            and data['results'][0] == check_data[2]
            and data['results'][1] == check_data[3]
        ), (
            f'Проверьте, что при GET запросе `{self.url}?page=2&limit=2` '
            'возвращаете корректные данные при указании номeра страницы и '
            'лимита для суперпользователя. '
            'Значение параметра `results` не правильное'
        )

    def user_data(self, id):
        return {
            'username': f'TestUser{id}', 'email': f'testuser{id}@fdgrm.fake',
            'password': 'zxcvbnm1234567890', 'first_name': f'user{id}',
            'last_name': f'user{id}'
        }

    @pytest.mark.django_db(transaction=True)
    def test_04_users_all_users_post(self, client, user_client,
                                     user_superuser_client):
        from django.contrib.auth import get_user_model

        user = get_user_model()

        data = {}
        whowhat = {
            'не авторизованный пользователь': client.post(self.url, data=data),
            'авторизованный польз-ль': user_client.post(self.url, data=data),
            'админ': user_superuser_client.post(self.url, data=data)
        }
        for who, response in whowhat.items():
            assert response.status_code == 400, (
                f'Проверь, что при POST запросе `{self.url}`, '
                f'c пустыми данными если {who}, возвращается статус 400'
            )
            for field in ('email', 'username', 'first_name',
                          'last_name', 'password'):
                assert response.json()[field] == ['Обязательное поле.'], (
                    f'Проверь, что при POST запросе `{self.url}`, '
                    f'если {who} не указал данные в поле {field} '
                    'возвращается ответ, что оно обязательно'
                )

        data = self.user_data(30)
        data['email'] = 'testsuperuser@fdgrm.fake',
        data['username'] = 'TestSuperuser'
        whowhat = {
            'не авторизованный пользователь': client.post(self.url, data=data),
            'авторизованный пол-тель': user_client.post(self.url, data=data),
            'админ': user_superuser_client.post(self.url, data=data)
        }
        for who, response in whowhat.items():
            assert response.status_code == 400, (
                f'Проверь, что при POST запросе `{self.url}`, '
                f'c существующими данными если {who}, возвращается статус 400'
            )
            for field in ('email', 'username'):
                assert 'уже существует' in response.json()[field][0], (
                    f'Проверь, что при POST запросе `{self.url}`, '
                    f'если {who} укзаал существующий {field} '
                    'возвращается ответ, что он уже есть'
                )

        notau_data = self.user_data(7)
        au_data = self.user_data(5)
        adm_data = self.user_data(6)
        whowhat = {
            'не авторизованный пользователь': (
                client.post(self.url, data=notau_data), 7
            ),
            'авторизованный пользователь': (
                user_client.post(self.url, data=au_data), 5
            ),
            'админ': (
                user_superuser_client.post(self.url, data=adm_data), 6
            )
        }
        for who, (response, id) in whowhat.items():
            assert response.status_code == 201, (
                f'Проверь, что при POST запросе `{self.url}`, '
                f'если {who}, возвращается статус 201'
            )
            assert user.objects.filter(username=f'TestUser{id}').exists(), (
                f'Проверь, что при POST запросе `{self.url}`, '
                f'если {who}, создается новый пользователь'
            )
            for param in ('email', 'username', 'first_name',
                          'last_name', 'password'):
                assert param in response.json(), (
                    f'Проверь, что при POST запросе `{self.url}`, '
                    f'если {who}, с правильными данными '
                    f'возвращает поле {param}.'
                )

    @pytest.mark.django_db(transaction=True)
    def test_05_check_permission_not_auth(self, client, create_users):
        create_users
        urls = (self.url_detail, self.url_me, self.url_pass)

        for url in urls:
            response = client.get(url)
            assert response.status_code == 401, (
                f'Проверь, что при GET запросе `{url}` '
                'без токена авторизации возвращается статус 401'
            )
            if url != self.url_detail:
                response = client.post(url)
                assert response.status_code == 401, (
                    f'Проверь, что при POST запросе `{url}` '
                    'без токена авторизации возвращается статус 401'
                )
            response = client.put(url)
            assert response.status_code == 401, (
                f'Проверь, что при PUT запросе `{url}` '
                'без токена авторизации возвращается статус 401'
            )
            response = client.patch(url)
            assert response.status_code == 401, (
                f'Проверь, что при PUT запросе `{url}` '
                'без токена авторизации возвращается статус 401'
            )

    @pytest.mark.django_db(transaction=True)
    def test_06_check_permission_auth(self, user_client, create_users):
        create_users
        urls = (self.url_detail, self.url_me, self.url_pass)

        for url in urls:
            if url == self.url_me:
                response = user_client.post(url)
                assert response.status_code == 405, (
                    f'Проверь, что при POST запросе `{url}` '
                    'c токеном авторизации возвращается статус 405'
                )
            if url == self.url_detail:
                response = user_client.put(url)
                assert response.status_code == 403, (
                    f'Проверь, что при PUT запросе `{url}` '
                    'c токеном авторизации возвращается статус 403'
                )
                response = user_client.patch(url)
                assert response.status_code == 403, (
                    f'Проверь, что при PATCH запросе `{url}` '
                    'c токеном авторизации возвращается статус 403'
                )
                response = user_client.delete(url)
                assert response.status_code == 403, (
                    f'Проверь, что при DELETE запросе `{url}` '
                    'c токеном авторизации возвращается статус 403'
                )
            if url != self.url_detail:
                response = user_client.put(url)
                assert response.status_code == 405, (
                    f'Проверь, что при PUT запросе `{url}` '
                    'c токеном авторизации возвращается статус 405'
                )
                response = user_client.patch(url)
                assert response.status_code == 405, (
                    f'Проверь, что при PATCH запросе `{url}` '
                    'c токеном авторизации возвращается статус 405'
                )
                response = user_client.delete(url)
                assert response.status_code == 405, (
                    f'Проверь, что при DELETE запросе `{url}` '
                    'c токеном авторизации возвращается статус 405'
                )

    @pytest.mark.django_db(transaction=True)
    def test_07_users_detail_auth_admin_get(self, user_client,
                                            user_superuser_client,
                                            create_users,
                                            user):
        from django.contrib.auth import get_user_model

        from interactions.models import Follow

        url_notexist = f'{self.url}100500/'
        user = get_user_model()
        main_data = create_users
        check_data = self.data_add_del(main_data, 'is_subscribed',
                                       False, 'password')

        responses = {
            'user': user_client.get(url_notexist),
            'admin': user_superuser_client.get(url_notexist)
        }
        for who, response in responses.items():
            assert response.status_code == 404, (
                'Проверь, что при GET запросе на '
                'не существующего пользователя '
                f'c токеном авторизации {who} возвращается статус 404'
            )
            assert ('detail' in response.json()
                    and isinstance(response.json()['detail'], str)), (
                'Проверь, что при GET запросе на '
                'не существующего пользователя '
                f'c токеном авторизации {who} описывается причина ошибки'
            )

        responses = {
            'user': user_client.get(self.url_detail),
            'admin': user_superuser_client.get(self.url_detail)
        }

        for who, response in responses.items():
            assert response.status_code == 200, (
                f'Проверь, что при GET запросе `{self.url_detail}` '
                f'c токеном авторизации {who} возвращается статус 200'
            )
            assert check_data[1] == response.json(), (
                f'Проверь, что при GET запросе `{self.url_detail}` '
                f'c токенoм авторизации {who} возвращаются корректные данные'
            )

        user_test = user.objects.get(username='TestUser')
        user_admin = user.objects.get(username='TestSuperuser')
        user2 = user.objects.get(id=1)
        follow1 = Follow.objects.create(user=user_test, author=user2)
        follow2 = Follow.objects.create(user=user_admin, author=user2)
        responses = {
            'user': (follow1, user_client.get(self.url_detail)),
            'admin': (follow2, user_superuser_client.get(self.url_detail))
        }
        for who, (follow, response) in responses.items():
            assert response.json()['is_subscribed'] is True, (
                f'Проверь, что при GET запросе `{self.url_detail}` '
                f'c токенoм авторизации {who} отопоражается true '
                'если автор подписан'
            )
            follow.delete()

    @pytest.mark.django_db(transaction=True)
    def test_08_users_detail_admin(self, user_superuser_client,
                                   create_users):
        from django.contrib.auth import get_user_model

        user = get_user_model()
        create_users

        data = {
            'username': 'TestUser500', 'email': 'testuser500@fdgrm.fake',
            'password': 'zxcvbnm1234567890', 'first_name': 'user500',
            'last_name': 'user500'
        }
        response = user_superuser_client.put(self.url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PUT запросе `{self.url_detail}` c токеном '
            'авторизации админа возвращается статус 200'
        )
        new_data = user_superuser_client.get(self.url_detail).json()
        new_data.pop('is_subscribed')
        new_data.pop('id')
        new_data['password'] = data['password']
        assert new_data == data, (
            'Проверь правильно ли работает метод PUT '
            f'c токеном админа в {self.url_detail}'
        )
        data = {'username': 'testtest'}
        response = user_superuser_client.patch(self.url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PATCH запросе `{self.url_detail}` '
            'c токеном авторизации админа возвращается статус 200'
        )
        assert user.objects.filter(username=data['username']).exists(), (
            'Проверь правильно ли работает метод PATCH '
            f'c токеном админа в {self.url_detail}'
        )
        response = user_superuser_client.delete(self.url_detail)
        assert response.status_code == 204, (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации админа возвращается статус 204'
        )
        assert not user.objects.filter(id=1).exists(), (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации админа пользователь удаляется'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_users_me_auth_admin_get(self, user_client,
                                        user_superuser_client):
        admin_data = {
            'username': 'TestSuperuser', 'email': 'testsuperuser@fdgrm.fake',
            'first_name': 'TestSuperuser', 'last_name': 'TestSuperuser'
        }
        user_data = {
            'username': 'TestUser', 'email': 'testuser@fdgrm.fake',
            'first_name': 'user', 'last_name': 'user bio'
        }
        responses = {
            'user': (user_client.get(self.url_me), user_data),
            'admin': (user_superuser_client.get(self.url_me), admin_data)
        }
        for who, (response, data) in responses.items():
            assert response.status_code == 200, (
                f'Проверь, что при GET запросе `{self.url_detail}` c токеном '
                f'авторизации {who} возвращается статус 200'
            )
            check_data = response.json()
            check_data.pop('id')
            check_data.pop('is_subscribed')
            assert check_data == data, (
                f'Проверь, что при GET запросе `{self.url_detail}` c токеном '
                f'авторизации {who} возвращаются корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_10_users_set_password_auth_admin_post(self, user_client,
                                                   user_superuser_client):
        data = {
            'new_password': "zxcvbnm1234567890",
            "current_password": "1234567"
        }
        responses = {
            'user': user_client.post(self.url_pass, data=data),
            'admin': user_superuser_client.post(self.url_pass, data=data)
        }
        for who, response in responses.items():
            assert response.status_code == 204, (
                f'Проверь, что при POST запросе `{self.url_pass}` c токеном '
                f'авторизации {who} возвращается статус 204'
            )
        data = {
            'new_password': "zxcvbnm1234567890",
            "current_password": "126876965"
        }
        responses = {
            'user': user_client.post(self.url_pass, data=data),
            'admin': user_superuser_client.post(self.url_pass, data=data)
        }
        for who, response in responses.items():
            field = 'current_password'
            assert response.status_code == 400, (
                f'Проверь, что при POST запросе `{self.url_pass}` '
                'c неправильным паролем, статус ответа 400'
            )
            assert (field in response.json().keys()
                    and isinstance(response.json()[field], list)), (
                f'Проверь, что при POST запросе `{self.url_pass}` '
                'c неправильным паролем, есть сообщение о том, '
                'какие поля заполенены неправильно'
            )
        data = {
            'new_password': "ыпр123",
            "current_password": "zxcvbnm1234567890"
        }
        responses = {
            'user': user_client.post(self.url_pass, data=data),
            'admin': user_superuser_client.post(self.url_pass, data=data)
        }
        for who, response in responses.items():
            field = 'new_password'
            assert (field in response.json().keys()
                    and isinstance(response.json()[field], list)), (
                f'Проверь, что при POST запросе `{self.url_pass}` '
                'c не валидным новым паролем, есть сообщение о том, '
                'какие поля заполенены неправильно'
            )
