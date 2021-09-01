from rest_framework import serializers
from . import models


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['name', 'message']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['content', 'date']
