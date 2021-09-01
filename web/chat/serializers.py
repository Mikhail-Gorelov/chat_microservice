from rest_framework import serializers
from . import models


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['id', 'username', 'message']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date']
