import os

from django.db import models
from django.dispatch import receiver

from .models import Chat


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
