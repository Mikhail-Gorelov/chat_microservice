from rest_framework import serializers

import main.models
from django.contrib.auth import get_user_model
from . import models, services
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from main.services import MainService
from .services import ChatService
from rest_framework.status import HTTP_400_BAD_REQUEST

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'author_id']


class RestAndWebsocketSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=50)

    def save(self, **kwargs):
        data = {
            "type": "chat.message",
            "data": {
                'command': 'new_message',
                'message': self.validated_data.get("message"),
                'username': self.validated_data.get("author"),
            },
        }
        async_to_sync(get_channel_layer().group_send)("general_room", data)


# тут нужно сделать сериалайзер UserChat, далее нужно сделать тут же валидацию ???
class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserChat
        fields = ['id', 'user_id', 'chat']

    def validate(self, data):
        chat_status = models.Chat.objects.get(id=data.get("chat").id).status
        print(chat_status)
        if chat_status == 0:
            raise serializers.ValidationError({'user': 'user not allowed in this chat'})
        return data

    def save(self, **kwargs):
        print(self.validated_data)
        user_chat = models.UserChat.objects.create(**self.validated_data)
        user_chat.save()
        return user_chat


class ChatSerializer(serializers.Serializer):
    user_id_1 = serializers.IntegerField(min_value=1, source="user_chat.user_id_1")
    user_id_2 = serializers.IntegerField(min_value=1, source="user_chat.user_id_2")
    name = serializers.CharField(required=False, default="")
    description = serializers.CharField(required=False, default="")

    def save(self, **kwargs):
        users: dict = self.validated_data.pop("user_chat")
        chat = models.Chat.objects.create(**self.validated_data)
        services.ChatService.add_users_to_chat(list(users.values()), chat)  # convert users to list
        return chat


class ChatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = "__all__"


class ChatSerializerCheck(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ("id", "name", "description", "status", "date", "file")


class MessageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ("content", "date", "chat", "author_status")

    # TODO: Продумать более хитрую валидацию, чтобы работало
    def validate(self, data):
        chat_status = models.Chat.objects.get(id=data.get("chat").chat).status
        print(chat_status)
        if chat_status == 0:
            raise serializers.ValidationError({'user': 'user not allowed in this chat'})
        return data

    def save(self, **kwargs):
        print(self.validated_data)
        user_chat = models.Message.objects.create(**self.validated_data)
        user_chat.save()
        return user_chat


class ChatInitSerializer(serializers.Serializer):
    auth = serializers.CharField()
    user_id = serializers.IntegerField(min_value=1)

    def validate_auth(self, auth: str):
        self.user_data: dict = ChatService.validate_user_jwt(auth, request=self.context['request'])
        # есть данные, вернуть в save
        return auth

    def save(self, **kwargs):
        # создать здесь комнату (id) user_data
        # создать комнату с jwt token (user_data id) и user_id
        # проверка есть ли комната с этим пользователем
        # актив / не актив комнат
        return self.user_data
        # ordereddict here
