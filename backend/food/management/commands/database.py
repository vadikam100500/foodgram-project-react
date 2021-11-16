import csv

from django.core.management.base import BaseCommand

from food.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        reader = csv.reader(
            open('data/ingredients.csv', 'r', encoding='utf-8')
        )
        for row in reader:
            Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1],
            )

        self.stdout.write(self.style.SUCCESS('Successfully load data'))
