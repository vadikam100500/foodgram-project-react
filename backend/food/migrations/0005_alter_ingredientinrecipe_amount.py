# Generated by Django 3.2.9 on 2021-12-07 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_recipe_recipe_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Количество ингредиента'),
        ),
    ]