# Generated by Django 3.2.4 on 2021-07-08 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20210707_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_recipes',
            name='percent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
