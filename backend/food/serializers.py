from django.contrib.auth import get_user_model
from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from interactions.models import Favorite, Purchase
from users.serializers import CustomUserGetSerializer

from .models import Ingredient, IngredientInRecipe, Recipe, Tag, TagInRecipe

User = get_user_model()


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

    def boolfield(self, request_obj, main_obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return main_obj.objects.filter(user=request.user,
                                       recipe=request_obj.id).exists()

    def get_is_favorited(self, obj):
        return self.boolfield(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.boolfield(obj, Purchase)

    def validate(self, data):
        author = self.context.get('request').user
        recipe_name = self.initial_data.get('name')
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        cooking_time = self.initial_data.get('cooking_time')
        method = self.context.get('request').method

        if cooking_time:
            if cooking_time is not int or cooking_time < 1:
                raise serializers.ValidationError(
                    'Время приготовления должно быть '
                    'больше минуты'
                )

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
            if amount is not int or amount <= 0:
                raise serializers.ValidationError(
                    'Убедитесь, что значение количества '
                    'ингредиента больше нуля'
                )
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
            ingrs_set.add(ingr_id)

    def tag_validate(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тэг'
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
            for tag_id in tags:
                recipe_tag = TagInRecipe.objects.create(
                    recipe=recipe,
                    tag_id=tag_id,
                )
                recipe_tag.save()

    def update(self, instance, validated_data):
        image = None
        ingredients = None
        tags = None
        try:
            image = validated_data.pop('image')
        except KeyError:
            pass
        try:
            ingredients = validated_data.pop('ingredients')
        except KeyError:
            pass
        try:
            tags = validated_data.pop('tags')
        except KeyError:
            pass
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if image:
            instance.image = image
        instance.save()
        self.ingrs_tags_update(ingredients, tags, instance)
        return instance

    def ingrs_tags_update(self, ingredients, tags, recipe):
        method = self.context.get('request').method
        with transaction.atomic():
            if method == 'PATCH':
                if ingredients:
                    IngredientInRecipe.objects.filter(recipe=recipe).delete()
                    for ingredient in ingredients:
                        ingr_amount = IngredientInRecipe.objects.create(
                            recipe=recipe,
                            ingredient_id=ingredient.get('id'),
                            amount=ingredient.get('amount')
                        )
                        ingr_amount.save()
                if tags:
                    TagInRecipe.objects.filter(recipe=recipe).delete()
                    for tag_id in tags:
                        recipe_tag = TagInRecipe.objects.create(
                            recipe=recipe,
                            tag_id=tag_id,
                        )
                        recipe_tag.save()
            else:
                IngredientInRecipe.objects.filter(recipe=recipe).delete()
                TagInRecipe.objects.filter(recipe=recipe).delete()
                self.ingrs_tags_create(ingredients, tags, recipe)


class RecipeLiteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'cooking_time')
