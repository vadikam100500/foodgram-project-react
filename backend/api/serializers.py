from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from drf_base64.fields import Base64ImageField
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from food.models import (Ingredient, IngredientInRecipe, Recipe, Tag,
                         TagInRecipe)
from interactions.models import Favorite, Follow, Purchase

User = get_user_model()


class CustomUserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password'
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')
        if password:
            try:
                validate_password(password, user)
            except django_exceptions.ValidationError as e:
                serializer_error = serializers.as_serializer_error(e)
                raise serializers.ValidationError(
                    {'password': serializer_error['non_field_errors']}
                )
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return User.objects.create_user(**validated_data)
        except IntegrityError:
            self.fail('Не удалось создать пользователя')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit')
            )
        ]


class TagInRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagInRecipe
        fields = ('id', 'name', 'color', 'slug')


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient'
                                                 '.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeLiteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagInRecipeGetSerializer(read_only=True, many=True,
                                    source='recipe_tag')
    author = CustomUserGetSerializer(read_only=True)
    ingredients = IngredientInRecipeGetSerializer(many=True,
                                                  read_only=True,
                                                  source='ingr_amount')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return self.bool_response(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.bool_response(obj, Purchase)

    def bool_response(self, request_obj, main_obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return main_obj.objects.filter(user=request.user,
                                       recipe=request_obj.id).exists()

    def validate(self, data):
        method = self.context.get('request').method
        author = self.context.get('request').user
        recipe_name = data.get('name')
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        if method in ('POST', 'PUT'):
            if (method == 'POST'
                and Recipe.objects.filter(author=author,
                                          name=recipe_name).exists()):
                raise serializers.ValidationError(
                    'Такой рецепт у вас уже есть!'
                )
            self.ingr_validate(ingredients)
            self.tag_validate(tags)

            if method == 'POST':
                data['author'] = author
            data['ingredients'] = ingredients
            data['tags'] = tags

        if method == 'PATCH':
            if ingredients:
                self.ingr_validate(ingredients)
                data['ingredients'] = ingredients
            if tags:
                self.tag_validate(tags)
                data['tags'] = tags
        return data

    def ingr_validate(self, ingredients):
        ingrs_set = set()
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингридиент'
            )
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingr_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingr_id).exists():
                raise serializers.ValidationError(
                    'Такого ингредиента еще нет, '
                    'обратитесь к администратору.'
                )
            if ingr_id in ingrs_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.'
                )
            try:
                int(amount)
            except ValueError:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть числом'
                )
            if int(amount) < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что значение количества '
                    'ингредиента больше единицы'
                )
            ingrs_set.add(ingr_id)

    def tag_validate(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тэг'
            )
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                'Тэги не должны повторяться'
            )
        for tag_id in tags:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    'Такого тэга еще нет, '
                    'обратитесь к администратору.'
                )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        with transaction.atomic():
            recipe = Recipe.objects.create(image=image,
                                           **validated_data)
        self.ingrs_tags_create(ingredients, tags, recipe)
        return recipe

    def ingrs_tags_create(self, ingredients, tags, recipe):
        self.ingrs_create(ingredients, recipe)
        self.tags_create(tags, recipe)

    def ingrs_create(self, ingredients, recipe):
        with transaction.atomic():
            for ingredient in ingredients:
                amount = ingredient.get('amount')
                if not amount:
                    amount = 0
                ingr_amount = IngredientInRecipe.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=amount
                )
                ingr_amount.save()

    def tags_create(self, tags, recipe):
        with transaction.atomic():
            for tag_id in tags:
                recipe_tag = TagInRecipe.objects.create(
                    recipe=recipe,
                    tag_id=tag_id,
                )
                recipe_tag.save()

    def update(self, instance, validated_data):
        attrs = {
            'image': None,
            'ingredients': None,
            'tags': None
        }
        for attr in attrs:
            if attr in validated_data:
                attrs[attr] = validated_data.pop(attr)

        if attrs['image']:
            instance.image = attrs['image']
        instance = super().update(instance, validated_data)

        self.ingrs_tags_update(attrs['ingredients'],
                               attrs['tags'], instance)
        return instance

    def ingrs_tags_update(self, ingredients, tags, recipe):
        method = self.context.get('request').method
        with transaction.atomic():
            if method == 'PATCH':
                if ingredients:
                    IngredientInRecipe.objects.filter(recipe=recipe).delete()
                    self.ingrs_create(ingredients, recipe)
                if tags:
                    TagInRecipe.objects.filter(recipe=recipe).delete()
                    self.tags_create(tags, recipe)
            else:
                IngredientInRecipe.objects.filter(recipe=recipe).delete()
                TagInRecipe.objects.filter(recipe=recipe).delete()
                self.ingrs_tags_create(ingredients, tags, recipe)


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        if self.Meta.model is Favorite:
            answer = 'избранном'
        else:
            answer = 'списке покупок'
        if (
            self.Meta.model.objects
            .select_related('recipe')
            .filter(user=request.user, recipe__id=recipe_id)
            .exists()
        ):
            raise serializers.ValidationError(f'Рецепт уже есть в {answer}')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeLiteSerializer(instance.recipe, context=context).data


class PurchaseSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Purchase


class SubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    @swagger_serializer_method(serializer_or_field=RecipeLiteSerializer)
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.author.recipes
        if limit:
            recipes = recipes.all()[:int(limit)]
        context = {'request': request}
        return RecipeLiteSerializer(recipes, context=context, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionsSerializer(instance, context=context).data
