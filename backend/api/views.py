from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from food.models import Ingredient, Recipe, Tag

from . import serializers
from .permissions import IsAdminUserOrReadOnly

User = get_user_model()


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = LimitOffsetPagination


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = LimitOffsetPagination
