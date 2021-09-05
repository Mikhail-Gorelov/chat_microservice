from django.db import models


class Author(models.Model):
    ONLINE = 'online'
    OFFLINE = 'offline'
    STATUS = (
        (ONLINE, 'On-line'),
        (OFFLINE, 'Off-line'),
    )
    status = models.CharField(
        max_length=10, choices=STATUS,
        default=OFFLINE
    )
    username = models.CharField(max_length=50, unique=True)
    objects = models.Manager()


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name='message')
    objects = models.Manager()
