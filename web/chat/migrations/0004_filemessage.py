# Generated by Django 3.2.10 on 2022-02-08 17:32

import chat.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_message_author_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to=chat.models.file_upload_to)),
                ('filename', models.CharField(max_length=100)),
                ('content_type', models.CharField(choices=[('.pdf', 'PDF'), ('.jpg', 'JPEG'), ('.mp3', 'MP3')], max_length=10)),
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='message_file', to='chat.message')),
            ],
        ),
    ]
