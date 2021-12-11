from rest_framework import serializers
from main.utils import find_dict_in_list
import main.models
import datetime
from datetime import timedelta
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


class UserChatShortSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        to_repr = super().to_representation(instance)
        output_list = list()
        if find_dict_in_list(self.context['user_data'], 'id', to_repr['user_id']) != {}:
            output_list.append(find_dict_in_list(self.context['user_data'], 'id', to_repr['user_id']))
        return find_dict_in_list(self.context['user_data'], 'id', to_repr['user_id'])

    class Meta:
        model = models.UserChat
        fields = ("user_id",)


class ChatListSerializer(serializers.ModelSerializer):
    user_chats = serializers.SerializerMethodField('get_users')
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    last_message = serializers.SerializerMethodField('get_last_message')
    last_message_date = serializers.SerializerMethodField('get_last_message_date')

    def get_users(self, obj):
        return UserChatShortSerializer(obj.user_chats, many=True, context=self.context).data

    def get_last_message(self, obj):
        return obj.last_message

    def get_last_message_date(self, obj):
        if obj.last_message_date:
            obj.last_message_date += timedelta(hours=2)
            return obj.last_message_date.strftime("%d-%m-%Y %H:%M:%S")
        return obj.last_message_date

    class Meta:
        model = models.Chat
        fields = (
            "id", "name", "description", "status", "date", "file", "last_message", "last_message_date", "user_chats")


class ChatSerializerCheck(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = ("id", "name", "description", "status", "date", "file")


class MessageListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        model = models.Message
        fields = ("content", "date", "chat", "author_status", "author_id")

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
        self.user_data: dict = ChatService.get_or_set_user_jwt(auth)
        return auth

    def save(self, **kwargs):
        chat = models.Chat.objects.filter(user_chats__user_id=self.user_data['id']).filter(
            user_chats__user_id=self.validated_data['user_id'])
        print(chat, "chat with users")
        if not chat.exists():
            new_chat = models.Chat.objects.create(
                name="Chat with user " + str(self.user_data['id']) + " and user " + str(self.validated_data['user_id']))
            models.UserChat.objects.bulk_create([
                models.UserChat(user_id=self.user_data['id'], chat=new_chat),
                models.UserChat(user_id=self.validated_data['user_id'], chat=new_chat),
            ])
            data = {
                "type": "add.chat",
                "data": {
                    'chat_id': str(new_chat.id),
                    'user': self.user_data['id'],
                },
            }
            async_to_sync(get_channel_layer().group_send)(f"events_for_user_{self.validated_data['user_id']}", data)
            print("I am in save chat init", f"events_for_user_{self.validated_data['user_id']}")
        return self.user_data


class ChatShortInfoSerializer(serializers.Serializer):
    user_id = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        print(validated_data)
        return ChatService.get_users_information(data=validated_data, request=self.context['request'])
