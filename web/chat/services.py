from typing import Any, OrderedDict, Union

from django.conf import settings
from django.db.models import OuterRef, Count, Subquery
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.cache import cache
from main.services import MainService
from . import models
from main.models import UserData
from channels.db import database_sync_to_async


class AsyncChatService:
    @staticmethod
    @database_sync_to_async
    def get_user(jwt_token: str):
        return ChatService.get_or_set_user_jwt(jwt_token)

    @staticmethod
    @database_sync_to_async
    def get_chat_list(user_id: int) -> list:
        return list(ChatService.get_chat_list(user_id).values_list('id', flat=True))


class ChatService:
    @staticmethod
    def add_users_to_chat(users: list, chat):
        objs = (models.UserChat(user_id=user, chat=chat) for user in users)
        models.UserChat.objects.bulk_create(objs)

    @staticmethod
    def create_chat(first_user: int, second_user: int):
        chat = models.Chat.objects.create(
            name="Chat with user " + str(first_user) + " and user " + str(second_user)
        )
        models.UserChat.objects.bulk_create(
            [
                models.UserChat(user_id=first_user, chat=chat),
                models.UserChat(user_id=second_user, chat=chat),
            ]
        )

        return chat

    @staticmethod
    def filter_chat_by_two_users(first_user_id: int, second_user_id: int):
        return models.Chat.objects.filter(user_chats__user_id=first_user_id).filter(
            user_chats__user_id=second_user_id
        )

    @staticmethod
    def get_chat_list(user_id: int):
        return models.Chat.objects.filter(user_chats__user_id=user_id)

    @staticmethod
    def get_last_message_from_chat(user_id: int):
        last_messages = models.Message.objects.filter(chat=OuterRef('id')).order_by('-pk')
        chat_queryset = ChatService.get_chat_list(user_id)
        queryset = chat_queryset.annotate(
            last_message=Subquery(last_messages.values('content')[:1]),
            last_message_date=Subquery(last_messages.values('date')[:1]),
        )
        return queryset

    @staticmethod
    def get_messages_in_chat(chat: int):
        return models.Message.objects.filter(chat=chat)

    @staticmethod
    def get_or_set_user_jwt(jwt: str):
        cache_key = cache.make_key('user_jwt', jwt)
        if data := cache.get(cache_key):
            return data
        url = '/jwt/callback/'
        service = MainService(url=url)
        response = service.service_response(method="post", data={"auth": jwt})
        if response.status_code == HTTP_400_BAD_REQUEST:
            raise ValidationError(response.data)
        cache.set(cache_key, response.data, timeout=600)
        return response.data

    @staticmethod
    def get_users_information(data: list, request):
        url = '/chat/user-information/'
        service = MainService(request=request, url=url)
        response = service.service_response(method="post", data={'user_id': data})
        return [UserData(**data)._asdict() for data in response.data]

    @staticmethod
    def get_chat_contacts(user_id: int) -> list[int]:
        user_chats = models.Chat.objects.filter(user_chats__user_id=user_id)
        users_id: list[int] = list(
            models.UserChat.objects.exclude(user_id=user_id)
            .filter(chat__in=user_chats)
            .values_list('user_id', flat=True)
            .distinct()
        )
        return users_id

    @staticmethod
    def get_chat_contacts_data(user_id: int, request):
        users_list: list[int] = []
        users_data: list[Union[dict[str, Any], OrderedDict[str, Any]]] = []
        users_id = ChatService.get_chat_contacts(user_id)
        for user in users_id:
            cache_key: str = cache.make_key('user', user)
            if cache_key not in cache:
                users_list.append(user)
            else:
                users_data.append(cache.get(cache_key))
        if users_list:
            response_data: list[
                Union[dict[str, Any], OrderedDict[str, Any]]
            ] = ChatService.get_users_information(data=users_list, request=request)
            for user in response_data:
                cache_key = cache.make_key('user', user['id'])
                cache.set(cache_key, user, timeout=600)
                users_data.append(user)
        return users_data
