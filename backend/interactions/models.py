from django.contrib.auth import get_user_model
from django.db import models

from food.models import Recipe

User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_subscriber',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_user_recept_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.recipe}" в избранном у {self.user}'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')
    subscription_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата подписки',
    )

    class Meta:
        ordering = ('-subscription_date',)
        verbose_name = 'подписку'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_not_follow_himself'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Рецепт'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ('-date_added',)
        verbose_name = 'покупку'
        verbose_name_plural = 'покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='purchase_user_recipe_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.recipe}" в списке покупок {self.user}'
