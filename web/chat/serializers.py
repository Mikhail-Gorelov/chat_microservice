from rest_framework import serializers
from . import models


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['id', 'username', 'message', 'status']


class MessageSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    author = serializers.CharField(source="author.username")

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'author']
