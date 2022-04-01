# Generated by Django 3.2.10 on 2022-02-15 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_alter_filemessage_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filemessage',
            name='content_type',
            field=models.CharField(choices=[('pdf', 'application/pdf'), ('jpg', 'image/jpeg'), ('mp3', 'audio/mpeg')], max_length=100),
        ),
    ]