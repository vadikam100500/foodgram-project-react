# Generated by Django 3.2.9 on 2021-11-22 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='name_unit_unique'),
        ),
    ]