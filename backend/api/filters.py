from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_filters import filters
from django_filters.fields import MultipleChoiceField
from django_filters.rest_framework.backends import DjangoFilterBackend
from django_filters.rest_framework.filterset import FilterSet

from food.models import Recipe

User = get_user_model()


class TagsMultipleChoiceField(MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'],
                                  code='required')
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )


class TagsFilter(filters.AllValuesMultipleFilter):
    field_class = TagsMultipleChoiceField


class RecipeFilter(FilterSet):
    tags = TagsFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(purchases__user=user)
        return queryset


class GlobalFilterBackend(DjangoFilterBackend):
    filterset_base = RecipeFilter
