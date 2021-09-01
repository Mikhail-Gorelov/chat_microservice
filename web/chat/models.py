from django.db import models


class Author(models.Model):
    username = models.CharField(max_length=50)
    objects = models.Manager()


class Message(models.Model):
    content = models.TextField(max_length=200)
    date = models.DateTimeField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name='message')
    objects = models.Manager()
