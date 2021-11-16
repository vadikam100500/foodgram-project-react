from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag, TagInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
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
        'name', 'author', 'text',
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


@admin.register(IngredientInRecipe)
class RecipeAndIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name',)


@admin.register(TagInRecipe)
class RecipeAndTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')
    list_filter = ('recipe__name',)
    search_fields = ('recipe__name',)
