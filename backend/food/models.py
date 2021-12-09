from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Название')
    color = ColorField(unique=True, verbose_name='Цвет в HEX')
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name='Уникальный слаг',
                            validators=[
                                RegexValidator(
                                    regex=r'^[-a-zA-Z0-9_]+$',
                                    message='Enter a valid slug'
                                )
                            ])

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_unit_unique'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    tags = models.ManyToManyField(Tag,
                                  through='TagInRecipe',
                                  verbose_name='Теги')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         verbose_name='Ингридиенты')
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Ссылка на картинку на сайте')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(в минутах)',
        validators=[MinValueValidator(1, message='Не менее 1')]
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='recipe_unique'
            )
        ]

    def __str__(self):
        return self.name


class TagInRecipe(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='recipe_tag',
                            verbose_name='Тег')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_tag',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'теги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='recipe_tag_unique'
            )
        ]

    def __str__(self):
        return f'Тэг "{self.tag}" рецепта "{self.recipe}".'


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingr_amount',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingr_amount',
                               verbose_name='Рецепт')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message='Не менее 1')],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        verbose_name = 'количество ингредиента'
        verbose_name_plural = 'количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='recipe_ingredient_unique'
            )
        ]

    def __str__(self):
        return f'Ингридиент "{self.ingredient}" рецепта "{self.recipe}".'
