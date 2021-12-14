import csv

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from djoser.serializers import SetPasswordSerializer
from djoser.views import TokenCreateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api import serializers
from api.decorators import multi_method_decorator
from api.docs.schemas import (EmptyAutoSchema, follower_params,
                              recipe_request_body)
from api.filters import GlobalFilterBackend
from api.pagination import FollowPagination, LimitPagination
from api.permissions import (IsAdminOrReadIfAuthenticatedObjPerm,
                             IsAdminOrReadOnly, RecipePermission)
from food.models import Ingredient, IngredientInRecipe, Recipe, Tag
from interactions.models import Favorite, Follow, Purchase

User = get_user_model()


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


@multi_method_decorator(
    names=['update', 'partial_update', 'destroy'],
    decorator=swagger_auto_schema(auto_schema=None)
)
class CustomUserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = serializers.CustomUserSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAdminOrReadIfAuthenticatedObjPerm,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return serializers.CustomUserGetSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscriptions':
            return serializers.SubscriptionsSerializer
        elif self.action == 'subscribe':
            return serializers.FollowSerializer
        return self.serializer_class

    @action(['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    @swagger_auto_schema(auto_schema=EmptyAutoSchema)
    def me(self, request, pk=None):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['post'], detail=False, permission_classes=(IsAuthenticated,))
    @swagger_auto_schema(request_body=SetPasswordSerializer,
                         responses={204: 'No Content'})
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False, pagination_class=FollowPagination,
            permission_classes=[IsAuthenticated])
    @swagger_auto_schema(responses={201: serializers.SubscriptionsSerializer})
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        if not queryset.exists():
            return Response({'error': 'Вы еще ни на кого не подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return Response(serializer.data)

    @action(['get'], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(manual_parameters=follower_params,
                         responses={201: serializers.SubscriptionsSerializer})
    def subscribe(self, request, pk=None):
        user, author = self.following_validate(request, pk)
        if not author:
            return Response({'error': user},
                            status=status.HTTP_400_BAD_REQUEST)

        data = {'user': user.id, 'author': author.id}
        serializer = self.get_serializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk=None):
        user, author, subscribe = self.following_validate(request, pk,
                                                          delete=True)
        if not author or not subscribe:
            return Response({'error': user},
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def following_validate(self, request, pk, delete=False):
        user = request.user
        if not User.objects.filter(id=pk).exists():
            if delete:
                return 'Такого пользователя еще нет', False, False
            return 'Такого пользователя еще нет', False
        author = get_object_or_404(User, id=pk)

        if delete:
            if not Follow.objects.filter(user=user, author=author).exists():
                return ('У вас еще нет этого пользователя в подписках',
                        True, False)
            else:
                return (user, author,
                        get_object_or_404(Follow, user=user,
                                          author=author))
        return user, author


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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )


@method_decorator(
    swagger_auto_schema(
        request_body=recipe_request_body,
        responses={201: serializers.RecipeSerializer}
    ),
    name='create'
)
@method_decorator(
    swagger_auto_schema(
        request_body=recipe_request_body,
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
    filter_backends = (GlobalFilterBackend,)
    filterset_fields = ('author', )

    def get_serializer_class(self):
        if self.action == 'favorite':
            return serializers.FavoriteSerializer
        elif self.action == 'shopping_cart':
            return serializers.PurchaseSerializer
        return self.serializer_class

    @action(['get'], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(responses={201: serializers.RecipeLiteSerializer})
    def favorite(self, request, pk=None):
        return self.alt_endpoint_create(request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.alt_endpoint_delete(request, pk, favorite=True)

    @action(['get'], detail=True, permission_classes=[IsAuthenticated])
    @swagger_auto_schema(responses={201: serializers.RecipeLiteSerializer})
    def shopping_cart(self, request, pk=None):
        return self.alt_endpoint_create(request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.alt_endpoint_delete(request, pk, cart=True)

    @action(['get'], detail=False, permission_classes=(IsAuthenticated,))
    @swagger_auto_schema(auto_schema=EmptyAutoSchema,
                         responses={200: 'Download', 401: 'NotAuthorized'})
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientInRecipe.objects
            .select_related('ingredient', 'recipe')
            .prefetch_related('purchases')
            .filter(recipe__purchases__user=request.user)
            .values_list('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Your_shopping_list.csv"')

        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
        for ingredient in ingredients:
            writer.writerow(ingredient)

        return response

    def alt_endpoint_create(self, request, pk):
        verdict, recipe, user = self.recipe_validate(request, pk)
        if not verdict:
            return recipe

        data = {
            'user': user.id,
            'recipe': recipe.id,
        }

        serializer = self.get_serializer(data=data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def alt_endpoint_delete(self, request, pk, favorite=False, cart=False):
        verdict, obj = self.recipe_validate(request, pk, delete=True,
                                            favorite=favorite, cart=cart)
        if not verdict:
            return obj
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def recipe_validate(self, request, pk, delete=False,
                        favorite=False, cart=False):
        user = request.user
        if not Recipe.objects.filter(id=pk).exists():
            return False, Response({'error': 'Такого рецепта еще нет'},
                                   status=status.HTTP_400_BAD_REQUEST), None
        recipe = get_object_or_404(Recipe, id=pk)

        if delete:
            model_answer = {
                'favorite': (Favorite, 'избранном'),
                'cart': (Purchase, 'списке покупок')
            }
            if favorite:
                model, answer = model_answer.get('favorite')
            if cart:
                model, answer = model_answer.get('cart')
            if not model.objects.filter(user=user, recipe=recipe).exists():
                return False, Response(
                    {'error': f'Такого рецепта еще нет в вашем {answer}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return True, get_object_or_404(model, user=user, recipe=recipe)

        return True, recipe, user
