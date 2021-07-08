# Generated by Django 3.2.4 on 2021-07-07 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_user_recipes_or_ingredient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_recipes',
            name='or_ingredient',
        ),
        migrations.AddField(
            model_name='user_ingredients',
            name='or_ingredient',
            field=models.BooleanField(default=False),
        ),
    ]
