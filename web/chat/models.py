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

    # def count_unread_messages(self):
    #     return self.messages.filter(
    #         ~models.Q(author_id__in=self.messages.values_list('author_id', flat=True))).aggregate(
    #         count=models.Count(
    #             "has_read", filter=models.Q(has_read=False)))

    def count_unread_messages(self, current_user_id: int):
        return self.messages.exclude(author_id=current_user_id).aggregate(
            count=models.Count(
                "has_read", filter=models.Q(has_read=False)))


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name='messages')
    author_id = models.PositiveIntegerField()
    has_read = models.BooleanField(default=False)

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

    # def count_unread(self):
    #     return self.chat.messages.filter(~models.Q(author_id=self.user_id)).aggregate(
    #         count=models.Count(
    #             "has_read", filter=models.Q(has_read=False))
    #     )
