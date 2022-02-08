from django.db.models import IntegerChoices, TextChoices
from django.utils.translation import gettext_lazy as _


class ChatStatus(IntegerChoices):
    OPEN = (1, _('Open'))
    CLOSE = (0, _('Close'))


class AuthorStatus(IntegerChoices):
    ONLINE = (1, _('Online'))
    OFFLINE = (0, _('Offline'))


class FileType(TextChoices):
    PDF = ('.pdf', 'PDF')
    JPEG = ('.jpg', 'JPEG')
    MP3 = ('.mp3', 'MP3')
