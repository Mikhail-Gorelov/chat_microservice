import os

from django.db import models
from uuid import uuid4

from django.dispatch import receiver

from chat.choices import ChatStatus, AuthorStatus


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    status = models.IntegerField(choices=ChatStatus.choices, default=ChatStatus.CLOSE)
    date = models.DateTimeField(auto_now_add=True)
    file = models.ImageField(upload_to="file_storage/")


@receiver(models.signals.post_delete, sender=Chat)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Chat` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Chat)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Chat` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Chat.objects.get(pk=instance.pk).file
    except Chat.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name='messages')
    author_id = models.PositiveIntegerField()
    author_status = models.IntegerField(choices=AuthorStatus.choices, default=AuthorStatus.OFFLINE)


class UserChat(models.Model):
    user_id = models.PositiveIntegerField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='user_chats')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user_id', 'chat',), name='Unique user in chat')
        ]
