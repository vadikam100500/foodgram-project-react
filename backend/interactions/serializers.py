from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from food.models import Recipe
from food.serializers import RecipeLiteSerializer

from .models import Favorite, Follow, Purchase

User = get_user_model()


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
