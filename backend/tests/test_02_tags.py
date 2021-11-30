import pytest


class Test02TagAPI:
    url = '/api/tags/'

    @pytest.mark.django_db(transaction=True)
    def test_01_tag_not_auth(self, create_tags, client):
        main_data = create_tags

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

        # permission
        assert client.post(self.url).status_code == 401, (
            f'Проверь, что Post запрос на `{self.url}.` не доступен'
        )

        # detail
        url_detail = f'{self.url}1/'
        detail_data = main_data[0]

        response = client.get(url_detail)
        assert response.status_code != 404, (
            f'Страница `{url_detail}.` не найдена, проверь этот адрес'
        )
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{url_detail}` '
            'без токена авторизации возвращается статус 200'
        )
        data = response.json()
        assert type(data) == dict, (
            f'Проверь, что при GET запросе `{url_detail}` '
            'возвращается 1 результат'
        )
        assert detail_data == data, (
            f'Проверь, что при GET запросе `{url_detail}` '
            'возвращаются корректные данные'
        )

        assert client.get(f'{self.url}2/').status_code == 200, (
            'Проверь, для всех ли тэгов доступна detail'
        )
        assert client.get(f'{self.url}3/').status_code == 200, (
            'Проверь, для всех ли тэгов доступна detail'
        )
        assert client.get(f'{self.url}10/').status_code == 404, (
            'Проверь, для всех ли тэгов доступна detail'
        )

        # permission detail
        assert client.patch(url_detail).status_code == 401, (
            f'Проверь, что PATCH запрос на `{url_detail}.` не доступен'
        )
        assert client.put(url_detail).status_code == 401, (
            f'Проверь, что PUT запрос на `{url_detail}.` не доступен'
        )
        assert client.delete(url_detail).status_code == 401, (
            'Проверь, что DELETE запрос на `{url_detail}.` не доступен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_tag_auth_user(self, user_client, create_tags):
        create_tags

        assert user_client.get(self.url).status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` c '
            'токеном авторизации возвращается статус 200'
        )

        # permission
        assert user_client.post(self.url).status_code == 403, (
            f'Проверь, что Post запрос на `{self.url}.` для '
            'авторизованного пользователя не доступен'
        )

        # detail
        url_detail = f'{self.url}1/'
        assert user_client.get(url_detail).status_code == 200, (
            f'Проверь, что при GET запросе `{url_detail}` с '
            'токеном авторизации возвращается статус 200'
        )

        # permisiion detail
        assert user_client.patch(url_detail).status_code == 403, (
            f'Проверь, что PATCH запрос на `{url_detail}.` '
            'не доступен для авторизованного пользователя'
        )
        assert user_client.put(url_detail).status_code == 403, (
            f'Проверь, что PUT запрос на `{url_detail}.` '
            'не доступен для авторизованного пользователя'
        )
        assert user_client.delete(url_detail).status_code == 403, (
            f'Проверь, что DELETE запрос на `{url_detail}.` '
            'не доступен для авторизованного пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_tag_admin_get_post(self, create_tags, user_superuser_client):
        main_data = create_tags

        response = user_superuser_client.get(self.url)
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}` '
            'c токеном авторизации админа возвращается статус 200'
        )

        data = {}
        response = user_superuser_client.post(self.url, data=data)
        assert response.status_code == 400, (
            f'Проверь, что при POST запросе `{self.url}` с не '
            'правильными данными с токеном админа возвращает статус 400'
        )
        empty_fields = ['name', 'slug']
        response_json = response.json()
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверь, что при POST запросе `{self.url}` '
                'без параметров, в ответе есть сообщение о том,'
                ' какие поля заполенены неправильно'
            )
        data = main_data[0]
        response = user_superuser_client.post(self.url, data=data)
        assert {
            'name': ['тег с таким Название уже существует.'],
            'color': ['тег с таким Цвет в HEX уже существует.'],
            'slug': ['тег с таким Уникальный слаг уже существует.']
        } == response.json(), (
            'Проверь, что нельзя создать 2 одинковых тэга с токеном админа'
        )
        data = {
            'name': 'Поздний завтрак',
            'slug': 'pozdniizavtrak',
            'color': '#49B642'
        }
        response = user_superuser_client.post(self.url, data=data)
        assert response.status_code == 201, (
            f'Проверь, что при POST запросе `{self.url}` '
            'с правильными данными и токеном админа возвращает статус 201'
        )

        # detail
        response = user_superuser_client.get(f'{self.url}1/')
        assert response.status_code == 200, (
            f'Проверь, что при GET запросе `{self.url}1/` c токеном '
            'авторизации админа возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_tag_admin_put_patch_delete(self, create_tags,
                                           user_superuser_client):
        from food.models import Tag

        create_tags
        url_detail = f'{self.url}1/'

        data = {'name': 'Завтрак2', 'slug': 'zavtrak2', 'color': '#15FF62'}
        response = user_superuser_client.put(url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PUT запросе `{url_detail}` c токеном '
            'авторизации админа возвращается статус 200'
        )
        data['id'] = 1
        assert user_superuser_client.get(url_detail).json() == data, (
            'Проверь правильно ли работает метод PUT '
            f'c токеном админа в {url_detail}'
        )

        data = {'name': 'Завтрак'}
        response = user_superuser_client.patch(url_detail, data=data)
        assert response.status_code == 200, (
            f'Проверь, что при PATCH запросе `{url_detail}` '
            'c токеном авторизации админа возвращается статус 200'
        )
        assert (user_superuser_client.get(url_detail).json()['name']
                == data['name']), ('Проверь правильно ли работает метод '
                                   f'PATCH c токеном админа в {url_detail}')
        response = user_superuser_client.delete(url_detail)
        assert response.status_code == 204, (
            f'Проверь, что при DELETE запросе `{url_detail}` '
            'c токеном авторизации админа возвращается статус 204'
        )
        assert not Tag.objects.filter(id=1).exists(), (
            f'Проверь, что при DELETE запросе `{url_detail}` '
            'c токеном авторизации админа тэг удаляется'
        )
