from django.db import models


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField()


class Author(models.Model):
    name = models.CharField(max_length=50)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='author')
