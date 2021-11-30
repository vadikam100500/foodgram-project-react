import pytest


@pytest.fixture
def create_users(django_user_model):
    result = []
    for id in range(10):
        data = {
            'username': f'TestUser{id}', 'email': f'testuser{id}@fdgrm.fake',
            'id': id, 'password': '1234567', 'first_name': f'user{id}',
            'last_name': f'user{id}'
        }
        result.append(data)
        django_user_model.objects.create_user(**data)
    return result


@pytest.fixture
def create_tags():
    from food.models import Tag

    data = [
        {'id': 1, 'name': 'Завтрак', 'slug': 'zavtrak', 'color': '#49B64E'},
        {'id': 2, 'name': 'Обед', 'slug': 'obed', 'color': '#49B643'},
        {'id': 3, 'name': 'Ужин', 'slug': 'uwin', 'color': '#49B644'}
    ]
    for tag in data:
        id, name, slug, color = tag.values()
        Tag.objects.create(id=id, name=name, slug=slug, color=color)
    return data


@pytest.fixture
def create_ingredient():
    from food.models import Ingredient

    data = [
        {'id': 3, 'name': 'жидкость', 'measurement_unit': 'л'},
        {'id': 2, 'name': 'овощь', 'measurement_unit': 'кг'},
        {'id': 1, 'name': 'фрукт', 'measurement_unit': 'шт'}
    ]
    for ingr in data:
        id, name, measurement_unit = ingr.values()
        Ingredient.objects.create(
            id=id, name=name, measurement_unit=measurement_unit
        )
    return data


@pytest.fixture
def create_recipes(create_users, create_tags, create_ingredient):
    from django.contrib.auth import get_user_model

    from food.models import IngredientInRecipe, Recipe, TagInRecipe

    user = get_user_model()

    users_data = create_users
    ingr_data = create_ingredient[::-1]
    tags_data = create_tags
    data_recipe = [{
        "id": num,
        "author": user.objects.get(id=num),
        "name": f"recipe {num}",
        "image": f"/recipes/image{num}.jpeg",
        "text": f"recipe{num}", "cooking_time": 100
    } for num in range(1, 4)]
    for recipe in data_recipe:
        id, author, name, image, text, cooking_time = recipe.values()
        Recipe.objects.create(
            id=id, author=author, name=name,
            image=image, text=text,
            cooking_time=cooking_time
        )
    data_tir = [{
        'id': num, 'recipe_id': num, 'tag_id': num
    } for num in range(1, 4)]
    for tir in data_tir:
        id, recipe_id, tag_id = tir.values()
        TagInRecipe.objects.create(
            id=id, recipe_id=recipe_id, tag_id=tag_id
        )
    data_iir = [{
        'id': num, 'amount': num * 10,
        'recipe_id': num, 'ingredient_id': num,
    } for num in range(1, 4)]
    for iir in data_iir:
        id, amount, recipe_id, ingredient_id = iir.values()
        IngredientInRecipe.objects.create(
            id=id, recipe_id=recipe_id,
            ingredient_id=ingredient_id, amount=amount
        )
    return data_recipe, data_tir, data_iir, users_data, ingr_data, tags_data
