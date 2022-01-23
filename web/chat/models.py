from uuid import uuid4

from django.db import models

from chat.choices import AuthorStatus, ChatStatus


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    status = models.IntegerField(choices=ChatStatus.choices, default=ChatStatus.CLOSE)
    date = models.DateTimeField(auto_now_add=True)
    file = models.ImageField(upload_to="file_storage/")


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name='messages')
    author_id = models.PositiveIntegerField()
    author_status = models.IntegerField(choices=AuthorStatus.choices, default=AuthorStatus.OFFLINE)

    class Meta:
        ordering = ('-date',)


class UserChat(models.Model):
    user_id = models.PositiveIntegerField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='user_chats')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user_id',
                    'chat',
                ),
                name='Unique user in chat',
            )
        ]
