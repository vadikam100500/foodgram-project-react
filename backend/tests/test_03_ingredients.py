import pytest


class Test03IngredientAPI:
    url = '/api/ingredients/'
    url_detail = '/api/ingredients/1/'

    @pytest.mark.django_db(transaction=True)
    def test_01_ingr_not_auth(self, client, create_ingredient):
        main_data = create_ingredient

        response = client.get(self.url)
        data = response.json()
        assert response.status_code != 404, (
            f'Страница `{self.url}.` не найдена, проверь этот адрес'
        )
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'без токена авторизации возвращается статус 200'
        )
        assert main_data == data, (
            f'Проверь, что при GET запросе `{self.url}` '
            'возвращаются корректные данные'
        )
        data = client.get(f'{self.url}?limit=1').json()
        assert 'results' not in data, (
            f'Проверь, что при GET запросе `{self.url}`'
            'выключена пагинация'
        )
        assert len(data) == len(main_data), (
            f'Проверь, что при GET запросе `{self.url}?limit=1` '
            'возвращаются все данные'
        )
        search = f'{self.url}?name=%D1%84%D1%80%D1%83'
        assert client.get(search).json() == [dict(main_data[2])], (
            f'Проверь, что для {self.url} включен поиск'
        )

        # permission
        assert client.post(self.url).status_code == 401, (
            f'Проверь, что POST запрос на `{self.url}.` не доступен'
        )

        # detail
        detail_data = dict(main_data[2])

        response = client.get(self.url_detail)
        assert response.status_code != 404, (
            f'Страница `{self.url_detail}.` не найдена, проверь этот адрес'
        )
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url_detail}`'
            'без токена авторизации возвращается статус 200'
        )
        data = response.json()
        assert type(data) == dict, (
            f'Проверь, что при GET запросе `{self.url_detail}` '
            'возвращается 1 результат'
        )
        assert detail_data == data, (
            f'Проверь, что при GET запросе `{self.url_detail}`'
            ' возвращаются корректные данные'
        )

        assert client.get(f'{self.url}2/').status_code == 200, (
            'Проверь, для всех ли ингридиентов доступна detail'
        )
        assert client.get(f'{self.url}3/').status_code == 200, (
            'Проверь, для всех ли ингридиентов доступна detail'
        )
        assert client.get(f'{self.url}10/').status_code == 404, (
            'Проверь, для всех ли ингридиентов доступна detail'
        )

        # permission detail
        assert client.patch(self.url_detail).status_code == 401, (
            f'Проверь, что PATCH запрос на `{self.url_detail}.` не доступен'
        )
        assert client.put(self.url_detail).status_code == 401, (
            f'Проверь, что PUT запрос на `{self.url_detail}.` не доступен'
        )
        assert client.delete(self.url_detail).status_code == 401, (
            f'Проверь, что DELETE запрос на `{self.url_detail}.` не доступен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_ingr_auth_user(self, user_client, create_ingredient):
        create_ingredient

        assert user_client.get(self.url).status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токеном авторизации возвращается статус 200'
        )

        # permission
        assert user_client.post(self.url).status_code == 403, (
            f'Проверь, что Post запрос на `{self.url}.` '
            'для авторизованного пользователя не доступен'
        )

        # detail
        assert user_client.get(self.url_detail).status_code == 200, (
            f'Проверь, что при GET запросе `{self.url_detail}` '
            'с токеном авторизации возвращается статус 200'
        )

        # permisiion detail
        assert user_client.patch(self.url_detail).status_code == 403, (
            f'Проверь, что PATCH запрос на `{self.url_detail}.` '
            'не доступен для авторизованного пользователя'
        )
        assert user_client.put(self.url_detail).status_code == 403, (
            f'Проверь, что PUT запрос на `{self.url_detail}.` '
            'не доступен для авторизованного пользователя'
        )
        assert user_client.delete(self.url_detail).status_code == 403, (
            f'Проверь, что DELETE запрос на `{self.url_detail}.` '
            'не доступен для авторизованного пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_ingr_admin_get_post(self, user_superuser_client,
                                    create_ingredient):

        create_ingredient

        response = user_superuser_client.get(self.url)
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` c токеном '
            'авторизации админа возвращается статус 200'
        )

        data = {}
        response = user_superuser_client.post(self.url, data=data)
        assert response.status_code == 400, (
            f'Проверь, что при POST запросе `{self.url}` с не правильными '
            'данными с токеном админа возвращает статус 400'
        )
        empty_fields = ['name', 'measurement_unit']
        response_json = response.json()
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверь, что при POST запросе `{self.url}` '
                'без параметров в ответе, есть сообщение о том, '
                'какие поля заполенены неправильно'
            )
        data = {'name': 'фрукт', 'measurement_unit': 'шт'}
        response = user_superuser_client.post(self.url, data=data)
        assert response.status_code != 201, (
            'Проверь, что нельзя создать 2 '
            'одинковых ингридиента с токеном админа '
        )
        assert response.status_code == 400, (
            'Проверь, что нельзя создать 2 одинковых'
            'ингридиента с токеном админа '
        )
        data = {'name': 'что-то класное', 'measurement_unit': 'много'}
        response = user_superuser_client.post(self.url, data=data)
        assert response.status_code == 201, (
            f'Проверь, что при POST запросе `{self.url}` с правильными'
            'данными и токеном админа возвращает статус 201'
        )

        # detail
        response = user_superuser_client.get(self.url_detail)
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url_detail}` '
            'c токеном авторизации админа возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_ingr_admin_put_patch_delete(self, user_superuser_client,
                                            create_ingredient):
        from food.models import Ingredient

        create_ingredient

        data = {'name': 'фрукт2', 'measurement_unit': '2шт'}
        response = user_superuser_client.put(self.url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PUT запросе `{self.url_detail}` c токеном '
            'авторизации админа возвращается статус 200'
        )
        data['id'] = 1
        assert user_superuser_client.get(self.url_detail).json() == data, (
            'Проверь правильно ли работает метод PUT '
            f'c токеном админа в {self.url_detail}'
        )
        data = {'name': 'фрукт'}
        response = user_superuser_client.patch(self.url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PATCH запросе `{self.url_detail}` '
            'c токеном авторизации админа возвращается статус 200'
        )
        assert (user_superuser_client.get(self.url_detail).json()['name']
                == data['name']), ('Проверь правильно ли работает метод PATCH '
                                   f'c токеном админа в {self.url_detail}')
        response = user_superuser_client.delete(self.url_detail)
        assert response.status_code == 204, (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации админа возвращается статус 204'
        )
        assert not Ingredient.objects.filter(id=1).exists(), (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации админа ингридиент удаляется'
        )
