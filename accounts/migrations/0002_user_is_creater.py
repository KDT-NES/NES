# Generated by Django 3.2.13 on 2022-11-30 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_creater',
            field=models.BooleanField(default=False),
        ),
    ]
