import pytest


class Test05RecipeAPI:
    url = '/api/recipes/'
    url_detail = '/api/recipes/1/'

    def data_add_del(self, data, what, what_value, pop=None):
        check_data = []
        for recipe_data in data:
            recipe_data[what] = what_value
            if pop:
                recipe_data.pop(pop)
            check_data.append(recipe_data)
        return check_data

    @pytest.mark.django_db(transaction=True)
    def test_01_recipe_main_get_all(self, client, user_client,
                                    user_superuser_client,
                                    create_recipes):

        (data_recipes, _, data_iirs, users_data,
         ingr_data, tags_data) = create_recipes
        check_data_users = self.data_add_del(users_data, 'is_subscribed',
                                             False, 'password')
        for ind in range(1, 4):
            data_recipes[ind - 1]['author'] = check_data_users[ind]
            ingr_data[ind - 1]['amount'] = data_iirs[ind - 1]['amount']
            data_recipes[ind - 1]['tags'] = [tags_data[ind - 1]]
            data_recipes[ind - 1]['ingredients'] = [ingr_data[ind - 1]]
            data_recipes[ind - 1]['image'] = ('http://testserver/media/'
                                              f'recipes/image{ind}.jpeg')
        check_data_recipes = self.data_add_del(
            self.data_add_del(data_recipes, 'is_favorited', False),
            'is_in_shopping_cart', False
        )[::-1]

        whowhat = {
            'не авторизованный польз-ль': client.get(self.url),
            'авторизованный польз-ль': user_client.get(self.url),
            'админ': user_superuser_client.get(self.url)
        }
        for who, response in whowhat.items():
            data = response.json()
            assert response.status_code != 404, (
                f'Страница `{self.url}` не найдена, '
                'проверь этот адрес в *urls.py*'
            )
            assert response.status_code == 200, (
                f'Проверь, что при GET запросе `{self.url}`, '
                f'если {who} возвращается статус 200'
            )
            assert type(data) == list, (
                f'Проверь, что при GET запросе `{self.url}` '
                f'если {who} возвращаемые данные в списке'
            )
            assert 'results' not in data, (
                f'Проверь, что при GET запросе `{self.url}` '
                f'для {who} возвращаете данные без  пагинации, '
                'если не указан параметр `limit`'
            )
            assert 'is_favorited' in data[0], (
                f'Проверь, что при GET запросе `{self.url}` '
                f'для {who}  есть параметр is_favorite'
            )
            assert 'is_in_shopping_cart' in data[0], (
                'Проверь, что при GET запросе `{self.url}` '
                f'для {who} есть параметр is_in_shopping_cart'
            )
            assert check_data_recipes == data, (
                f'Проверь, что при GET запросе `{self.url}` '
                f'для {who} возвращаются корректные данные'
            )
        whowhat = {
            'не авторизованный польз-ль': client.get(f'{self.url}?limit=2'),
            'авторизованный польз-ль': user_client.get(f'{self.url}?limit=2'),
            'админ': user_superuser_client.get(f'{self.url}?limit=2')
        }
        for who, response in whowhat.items():
            data = response.json()
            for param in ('count', 'next', 'previous', 'results'):
                assert param in data, (
                    f'Проверь, что при GET запросе `{self.url}?limit=2` '
                    f'для {who} возвращаете данные с пагинацией. '
                    f'Не найден параметр `{param}`'
                )
                assert data['count'] == 3, (
                    f'Проверь, что при GET запросе `{self.url}?limit=2` '
                    f'для {who} возвращаете данные с пагинацией. '
                    'Значение параметра `count` не правильное'
                )
                assert (
                    len(data['results']) == 2
                    and data['results'][0] == check_data_recipes[0]
                    and data['results'][1] == check_data_recipes[1]
                ), (
                    f'Проверь, что при GET запросе `{self.url}?limit=2` '
                    f'для {who} возвращаете данные с пагинацией. '
                    'Значение параметра `results` не правильное'
                )
        whowhat = {
            'не авторизованный польз-ль': client.get(f'{self.url}?'
                                                     'page=2&limit=2'),
            'авторизованный польз-ль': user_client.get(f'{self.url}?'
                                                       'page=2&limit=2'),
            'админ': user_superuser_client.get(f'{self.url}?page=2&limit=2')
        }
        for who, response in whowhat.items():
            data = response.json()
            assert (
                len(data['results']) == 1
                and data['results'][0] == check_data_recipes[2]
            ), (
                f'Проверь, что при GET запросе `{self.url}?page=2&limit=2` '
                f'для {who} возвращаете корректные данные при указании '
                'номера страницы и лимита. Значение параметра `results` '
                'не правильное'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_recipe_main_get_all_filtering(self, client, user_client,
                                              user_superuser_client,
                                              create_recipes):
        from django.contrib.auth import get_user_model

        from food.models import Recipe
        from interactions.models import Favorite, Purchase

        user = get_user_model()
        (data_recipes, _, data_iirs, users_data,
         ingr_data, tags_data) = create_recipes
        check_data_users = self.data_add_del(users_data, 'is_subscribed',
                                             False, 'password')
        for ind in range(1, 4):
            data_recipes[ind - 1]['author'] = check_data_users[ind]
            ingr_data[ind - 1]['amount'] = data_iirs[ind - 1]['amount']
            data_recipes[ind - 1]['tags'] = [tags_data[ind - 1]]
            data_recipes[ind - 1]['ingredients'] = [ingr_data[ind - 1]]
            data_recipes[ind - 1]['image'] = ('http://testserver/media/'
                                              f'recipes/image{ind}.jpeg')
        check_data_recipes = self.data_add_del(
            self.data_add_del(data_recipes, 'is_favorited', False),
            'is_in_shopping_cart', False
        )
        whowhat = {
            'не авторизованный польз-ль': client.get(f'{self.url}?'
                                                     'author=1'),
            'авторизованный польз-ль': user_client.get(f'{self.url}?'
                                                       'author=1'),
            'админ': user_superuser_client.get(f'{self.url}?author=1')
        }
        for who, response in whowhat.items():
            data = response.json()
            assert (
                len(data) == 1
                and data[0] == check_data_recipes[0]
            ), (
                f'Проверь, что при GET запросе `{self.url}?author=1` '
                f'для {who} возвращаете корректные данные при указании '
                'фильтрации по автору.'
            )
        whowhat = {
            'не авторизованный польз-ль': client.get(f'{self.url}?'
                                                     'tags=zavtrak'
                                                     '&tags=obed'),
            'авторизованный польз-ль': user_client.get(f'{self.url}?'
                                                       'tags=zavtrak'
                                                       '&tags=obed'),
            'админ': user_superuser_client.get(f'{self.url}?'
                                               'tags=zavtrak'
                                               '&tags=obed')
        }
        for who, response in whowhat.items():
            data = response.json()
            assert (
                len(data) == 2
                and data[0] == check_data_recipes[1]
                and data[1] == check_data_recipes[0]
            ), (
                f'Проверь, что при GET запросе `{self.url}?author=1` '
                f'для {who} возвращаете корректные данные при указании '
                'фильтрации по тэгам'
            )

        user_test = user.objects.get(username='TestUser')
        user_admin = user.objects.get(username='TestSuperuser')
        recipe = Recipe.objects.get(id=1)
        favorite1 = Favorite.objects.create(user=user_test, recipe=recipe)
        favorite2 = Favorite.objects.create(user=user_admin, recipe=recipe)
        responses = {
            'user': (favorite1, user_client.get(
                f'{self.url}?is_favorited=true'
            )),
            'admin': (favorite2, user_superuser_client.get(
                f'{self.url}?is_favorited=true'
            ))
        }
        for who, (favorite, response) in responses.items():
            data = response.json()
            check_data_recipes[0]['is_favorited'] = True
            assert (
                len(data) == 1
                and data[0] == check_data_recipes[0]
            ), (
                f'Проверь, что при GET запросе `{self.url}?is_favorited=true` '
                f'для {who} возвращаете корректные данные при указании '
                'фильтрации по избранному'
            )
            favorite.delete()
        cart1 = Purchase.objects.create(user=user_test, recipe=recipe)
        cart2 = Purchase.objects.create(user=user_admin, recipe=recipe)
        responses = {
            'user': (cart1, user_client.get(f'{self.url}?'
                                            'is_in_shopping_cart=true')),
            'admin': (cart2, user_superuser_client.get(f'{self.url}?'
                                                       'is_in_shopping'
                                                       '_cart=true'))
        }
        check_data_recipes[0]['is_favorited'] = False
        check_data_recipes[0]['is_in_shopping_cart'] = True
        for who, (cart, response) in responses.items():
            data = response.json()
            assert (
                len(data) == 1
                and data[0] == check_data_recipes[0]
            ), (
                f'Проверь, что при GET запросе '
                '`{self.url}?is_in_shopping_cart=1` '
                f'для {who} возвращаете корректные данные при указании '
                'фильтрации по корзине'
            )
            cart.delete()

    @pytest.mark.django_db(transaction=True)
    def test_03_recipe_detail_get_all(self, client, user_client,
                                      user_superuser_client,
                                      create_recipes):

        (data_recipes, _, data_iirs, users_data,
         ingr_data, tags_data) = create_recipes
        check_data_users = self.data_add_del(users_data, 'is_subscribed',
                                             False, 'password')
        for ind in range(1, 4):
            data_recipes[ind - 1]['author'] = check_data_users[ind]
            ingr_data[ind - 1]['amount'] = data_iirs[ind - 1]['amount']
            data_recipes[ind - 1]['tags'] = [tags_data[ind - 1]]
            data_recipes[ind - 1]['ingredients'] = [ingr_data[ind - 1]]
            data_recipes[ind - 1]['image'] = ('http://testserver/media/'
                                              f'recipes/image{ind}.jpeg')
        check_data_recipes = self.data_add_del(
            self.data_add_del(data_recipes, 'is_favorited', False),
            'is_in_shopping_cart', False
        )
        whowhat = {
            'не авторизованный польз-ль': client.get(self.url_detail),
            'авторизованный польз-ль': user_client.get(self.url_detail),
            'админ': user_superuser_client.get(self.url_detail)
        }
        for who, response in whowhat.items():
            data = response.json()
            assert response.status_code != 404, (
                f'Страница `{self.url_detail}` не найдена, '
                'проверь этот адрес в *urls.py*'
            )
            assert response.status_code == 200, (
                f'Проверь, что при GET запросе `{self.url_detail}`, '
                f'если {who} возвращается статус 200'
            )
            assert check_data_recipes[0] == data, (
                f'Проверь, что при GET запросе `{self.url_detail}` '
                f'для {who} возвращаются корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_04_recipe_not_auth_permission(self, client, create_recipes):
        create_recipes
        response = client.post(self.url)
        assert response.status_code == 401, (
            f'Проверь, что при POST запросе `{self.url}` '
            'без токена авторизации возвращается статус 401'
        )
        response = client.get(self.url_detail)
        assert response.status_code != 404, (
            f'Страница `{self.url_detail}` не найдена, '
            'проверь этот адрес в *urls.py*'
        )
        response = client.put(self.url_detail)
        assert response.status_code == 401, (
            f'Проверь, что при PUT запросе `{self.url_detail}` '
            'без токена авторизации возвращается статус 401'
        )
        response = client.patch(self.url_detail)
        assert response.status_code == 401, (
            f'Проверь, что при PATCH запросе `{self.url_detail}` '
            'без токена авторизации возвращается статус 401'
        )
        response = client.delete(self.url_detail)
        assert response.status_code == 401, (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_recipe_auth_not_owner_permission(self, user_client,
                                                 create_recipes):
        create_recipes
        response = user_client.put(self.url_detail)
        assert response.status_code == 403, (
            f'Проверь, что при PUT запросе `{self.url_detail}` '
            'не автора рецпета возвращается статус 403'
        )
        # response = user_client.patch(self.url_detail)
        # assert response.status_code == 403, (
        #     f'Проверь, что при PATCH запросе `{self.url_detail}` '
        #     'возвращается статус 403'
        # )
        response = user_client.delete(self.url_detail)
        assert response.status_code == 403, (
            f'Проверь, что при DELETE запросе `{self.url_detail}` '
            'возвращается статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_06_recipe_main_post_all(self, user_client,
                                     user_superuser_client,
                                     create_ingredient,
                                     create_tags, user,
                                     user_superuser):
        import json

        from food.models import IngredientInRecipe, Recipe, TagInRecipe

        create_ingredient, create_tags
        data = {
            'name': 'string',
            'text': 'string',
            'cooking_time': 5,
            'image': ('data:image/png;base64,iVBORw0KGgoA'
                      'AAANSUhEUgAAAAEAAAABAgMAAABieywaAA'
                      'AACVBMVEUAAAD///9fX1/S0ecCAAAACXBI'
                      'WXMAAA7EAAAOxAGVKw4bAAAACklEQVQImW'
                      'NoAAAAggCByxOyYQAAAABJRU5ErkJggg=='),
            'tags': [1, 2],
            'ingredients': [{'id': 1, 'amount': 10}]
        }
        responses = {
            'user': (user_client.post(self.url, data=json.dumps(data),
                                      content_type="application/json"),
                     user),
            'admin': (
                user_superuser_client.post(self.url, data=json.dumps(data),
                                           content_type="application/json"),
                user_superuser
            )
        }
        for who, (response, client) in responses.items():
            print(response.json())
            assert response.status_code == 201, (
                f'Проверь, что при POST запросе `{self.url}` c токеном '
                f'авторизации {who} возвращается статус 201'
            )
            assert Recipe.objects.filter(
                name=data['name'], text=data['text'],
                cooking_time=data['cooking_time']
            ).exists(), (
                f'Проверь что что при POST запросе `{self.url}` c токеном '
                f'авторизации {who} рецепт создался в базе'
            )
            recipe = Recipe.objects.get(name='string', author=client)
            assert TagInRecipe.objects.filter(recipe=recipe).exists(), (
                f'Проверь что что при POST запросе `{self.url}` c токеном '
                f'авторизации {who} рецепт создался в базе правильно.'
                'Нет данных в промежуточно таблице рецептов.'
            )
            assert IngredientInRecipe.objects.filter(recipe=recipe).exists(), (
                f'Проверь что что при POST запросе `{self.url}` c токеном '
                f'авторизации {who} рецепт создался в базе правильно.'
                'Нет данных в промежуточно таблице ингидиентов.'
            )
            recipe.delete()

    @pytest.mark.django_db(transaction=True)
    def test_07_recipe_detail_admin_patch(self, user_superuser_client,
                                          create_recipes):
        from food.models import Recipe

        create_recipes
        data = {'name': 'admin_MFKA'}
        user_superuser_client.patch(self.url_detail, data=data)
        assert Recipe.objects.filter(name='admin_MFKA').exists(), (
            f'Проверь что что при PATCH запросе `{self.url_detail}` c токеном '
            'админа рецепт обновился'
        )
        assert not Recipe.objects.filter(name='recipe 1').exists(), (
            f'Проверь что что при PATCH запросе `{self.url_detail}` c токеном '
            'админа старый рецепт удалился'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_recipe_detail_author_and_admin(self, user_client,
                                               user_superuser_client,
                                               create_ingredient,
                                               create_tags, create_recipes):
        import json

        from food.models import Recipe

        create_ingredient, create_tags
        data = {
            "ingredients": [{"id": 1, "amount": 10}],
            "tags": [1, 2],
            "image": ("data:image/png;base64,iVBORw0KGgoA"
                      "AAANSUhEUgAAAAEAAAABAgMAAABieywaAA"
                      "AACVBMVEUAAAD///9fX1/S0ecCAAAACXBI"
                      "WXMAAA7EAAAOxAGVKw4bAAAACklEQVQImW"
                      "NoAAAAggCByxOyYQAAAABJRU5ErkJggg=="),
            "name": "string",
            "text": "string",
            "cooking_time": 1
        }
        response = user_client.post(self.url, data=json.dumps(data),
                                    content_type="application/json")
        url_detail = f'{self.url}6/'
        data_new = {
            "ingredients": [{"id": 2, "amount": 20}],
            "tags": [2, 3],
            "image": ("data:image/png;base64,iVBORw0KGgoA"
                      "AAANSUhEUgAAAAEAAAABAgMAAABieywaAA"
                      "AACVBMVEUAAAD///9fX1/S0ecCAAAACXBI"
                      "WXMAAA7EAAAOxAGVKw4bAAAACklEQVQImW"
                      "NoAAAAggCByxOyYQAAAABJRU5ErkJggg=="),
            "name": "string_new",
            "text": "string_new",
            "cooking_time": 100500
        }
        response = user_client.put(url_detail, data=json.dumps(data_new),
                                   content_type="application/json")
        assert response.status_code == 200, (
            f'Проверь, что при PUT запросе `{self.url_detail}` c токеном '
            'авторизации автора возвращается статус 200'
        )
        assert Recipe.objects.filter(id=6, name=data_new['name']).exists(), (
            f'Проверь что что при PUT запросе `{self.url_detail}` '
            'c токеном авторизации автора рецепт обновился'
        )
        response = user_superuser_client.put(url_detail, data=json.dumps(data),
                                             content_type="application/json")
        assert response.status_code == 200, (
            f'Проверь, что при PUT запросе `{self.url_detail}` c токеном '
            'авторизации админа возвращается статус 200'
        )
        assert Recipe.objects.filter(id=6, name=data['name']).exists(), (
            f'Проверь что что при PUT запросе `{self.url_detail}` '
            'c токеном авторизации админа рецепт обновился'
        )
        data = {'name': 'blablabla'}
        # assert user_client.patch(url_detail,
        #                          data=data_new).status_code == 403, (
        #     'Проверь, что метод PATCH запрещен '
        #     f'для владельца на {self.url_detail}'
        # )
        response = user_client.delete(url_detail)
        assert response.status_code == 204, (
            f'Проверь что что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации автора возвращается статус 204'
        )
        assert not Recipe.objects.filter(id=6, name=data['name']).exists(), (
            f'Проверь что что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации автора рецепт удалился'
        )
        user_superuser_client.post(self.url, data=json.dumps(data_new),
                                   content_type="application/json")
        url_detail = f'{self.url}7/'
        response = user_superuser_client.delete(url_detail)
        assert response.status_code == 204, (
            f'Проверь что что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации автора возвращается статус 204'
        )
        assert not Recipe.objects.filter(id=7, name=data['name']).exists(), (
            f'Проверь что что при DELETE запросе `{self.url_detail}` '
            'c токеном авторизации автора рецепт удалился'
        )
