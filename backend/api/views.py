from django.contrib.auth import get_user_model, tokens
from django.utils.decorators import method_decorator
from djoser.serializers import SetPasswordSerializer
from djoser.views import TokenCreateView, TokenDestroyView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from food.models import Ingredient, Recipe, Tag
from users.serializers import CustomUserGetSerializer, CustomUserSerializer

from . import serializers
from .decorators import multi_method_decorator, request_body
from .pagination import LimitPagination
from .permissions import (IsAdminOrReadIfAuthenticatedObjPerm,
                          IsAdminOrReadOnly, RecipePermission)

User = get_user_model()


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class CustomTokenDestroyView(TokenDestroyView):

    def post(self, request):
        response = super().post(request)
        response.status_code = status.HTTP_201_CREATED
        return response


@multi_method_decorator(
    names=['update', 'partial_update', 'destroy'],
    decorator=swagger_auto_schema(auto_schema=None)
)
class CustomUserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAdminOrReadIfAuthenticatedObjPerm,)
    token_generator = tokens.default_token_generator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return CustomUserGetSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return self.serializer_class

    @action(['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request, pk=None):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False,
            permission_classes=(IsAuthenticated,))
    @swagger_auto_schema(request_body=SetPasswordSerializer,
                         responses={204: 'No Content'})
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@multi_method_decorator(
    names=['create', 'update', 'partial_update', 'destroy'],
    decorator=swagger_auto_schema(auto_schema=None)
)
class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


@multi_method_decorator(
    names=['create', 'update', 'partial_update', 'destroy'],
    decorator=swagger_auto_schema(auto_schema=None)
)
class IngredientsViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


@method_decorator(
    swagger_auto_schema(
        request_body=request_body,
        responses={201: serializers.RecipeSerializer}
    ),
    name='create'
)
@method_decorator(
    swagger_auto_schema(
        request_body=request_body,
        responses={200: serializers.RecipeSerializer}
    ),
    name='update'
)
@method_decorator(
    swagger_auto_schema(auto_schema=None),
    name='partial_update'
)
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = (RecipePermission,)
