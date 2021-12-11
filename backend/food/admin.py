from django.contrib import admin
from django.utils.html import format_html

from .models import Ingredient, IngredientInRecipe, Recipe, Tag, TagInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id', 'name', 'slug', 'color', 'preview')
    list_filter = ('name',)
    search_fields = ('name',)

    def preview(self, obj):
        return format_html(
            f'<span style="color:{obj.color}; '
            f'width=20px; height=20px;">{obj.name}</span>'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientInRecipeAdmin(admin.TabularInline):
    model = IngredientInRecipe
    extra = 2


class TagInRecipeAdmin(admin.StackedInline):
    model = TagInRecipe
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'recipe_image',
        'pub_date', 'cooking_time', 'favorite'
    )
    list_select_related = True
    readonly_fields = ('favorite',)
    list_filter = ('author__username', 'name', 'tags')
    search_fields = ('name',)
    save_on_top = True
    inlines = [IngredientInRecipeAdmin, TagInRecipeAdmin]

    @admin.display(description='В избранном')
    def favorite(self, obj):
        return obj.favorite_recipe.count()

    def recipe_image(self, obj):
        return format_html(
            f'<img src="{obj.image.url}" width=50px; height=50px;>'
        )


@admin.register(IngredientInRecipe)
class RecipeAndIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name',)


@admin.register(TagInRecipe)
class RecipeAndTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag')
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name',)
