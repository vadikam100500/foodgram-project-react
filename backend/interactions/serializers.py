from django.contrib.auth import get_user_model
from rest_framework import serializers

from food.models import Recipe
from food.serializers import RecipeLiteSerializer

from .models import Favorite, Purchase

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
