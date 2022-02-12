import datetime
import os
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.conf import settings
from main.models import UserData
from main.services import MainService
from main.utils import find_dict_in_list

from . import models, services
from .services import ChatService

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
        # ????!!!!
        # message = models.Message.objects.get(
        #     content=self.validated_data.get("message"), author_id=int(self.validated_data.get("author"))
        # )
        # print(self.validated_data['message'], "rest and websocket serializer")
        # ????!!!!
        async_to_sync(get_channel_layer().group_send)("general room", data)


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


class UserChatShortSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        to_repr = super().to_representation(instance)
        return find_dict_in_list(self.context['user_data'], 'id', to_repr['user_id'])

    class Meta:
        model = models.UserChat
        fields = ("user_id",)


class ChatListSerializer(serializers.ModelSerializer):
    user_chats = serializers.SerializerMethodField('get_users')
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    last_message = serializers.SerializerMethodField('get_last_message')
    last_message_date = serializers.SerializerMethodField('get_last_message_date')
    count_unread = serializers.SerializerMethodField('get_unread')
    interlocutor_online = serializers.SerializerMethodField('get_interlocutor_online')

    def get_users(self, obj):
        return UserChatShortSerializer(obj.user_chats, many=True, context=self.context).data

    def get_last_message(self, obj):
        return obj.last_message

    def get_last_message_date(self, obj):
        if obj.last_message_date:
            obj.last_message_date += timedelta(hours=2)
            return obj.last_message_date.strftime("%d-%m-%Y %H:%M:%S")
        return obj.last_message_date

    def get_interlocutor_online(self, obj):
        user_id = obj.user_chats.exclude(user_id=self.context['user'].id).values_list('user_id', flat=True)[0]
        data = settings.REDIS_DATABASE.hgetall(str(user_id))
        new_data = {key.decode(): val.decode() for key, val in data.items()}
        return new_data

    def get_unread(self, obj: models.Chat) -> int:
        return obj.count_unread_messages(self.context['user'].id)['count']

    class Meta:
        model = models.Chat
        fields = (
            "id",
            "name",
            "description",
            "status",
            "date",
            "file",
            "last_message",
            "last_message_date",
            "user_chats",
            "count_unread",
            "interlocutor_online",
        )


class ChatSerializerCheck(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ("id", "name", "description", "status", "date", "file")


class MessageListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        model = models.Message
        fields = ("id", "has_read", "content", "date", "chat", "author_id")

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
        user: dict = ChatService.get_or_set_user_jwt(auth)
        self.user_data = UserData(**user)
        return auth

    def save(self, **kwargs):
        current_user: UserData = self.user_data
        partner_user = self.validated_data['user_id']
        chat = ChatService.filter_chat_by_two_users(current_user.id, partner_user)
        print(chat, "chat with users")
        if not chat.exists():
            new_chat = ChatService.create_chat(current_user.id, partner_user)
            data = {
                "type": "add.chat",
                "data": {
                    'chat_id': str(new_chat.id),
                    'user': current_user._asdict(),
                },
            }
            async_to_sync(get_channel_layer().group_send)(
                f"events_for_user_{self.validated_data['user_id']}", data
            )
        return self.user_data


class ChatShortInfoSerializer(serializers.Serializer):
    user_id = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        print(validated_data)
        return ChatService.get_users_information(data=validated_data, request=self.context['request'])


class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = models.Chat
        fields = ['file']

    # def validate(self, attrs):
    #     limit = 4 * 1024 * 1024  # 4 mb
    #     if attrs.get('image').size > limit:
    #         raise serializers.ValidationError('File too large. Size should not exceed 4 MiB.')
    #     return attrs

    def to_representation(self, instance):
        return {'message': str(self.message.content), 'file_message': self.file_message.filename}

    def save(self, **kwargs):
        self.message = self.instance.messages.create(content='', author_id=1)  # TODO: NO HARDCODE
        self.file_message = models.FileMessage.objects.create(message=self.message, file=self.validated_data['file'],
                                                              filename="check", content_type="jpg")
        request = self.context['request']
        async_to_sync(get_channel_layer().group_send)(
            str(self.instance.pk), {
                "type": "file.message",
                "data": {
                    "file": request.build_absolute_uri(self.file_message.file.url),
                    "message_id": str(self.file_message.message.pk),
                    "filename": self.file_message.filename,
                    "content_type": self.file_message.content_type,
                }
            }
        )
        return
