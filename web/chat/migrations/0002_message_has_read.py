# Generated by Django 3.2.10 on 2022-01-29 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='has_read',
            field=models.BooleanField(default=False),
        ),
    ]
