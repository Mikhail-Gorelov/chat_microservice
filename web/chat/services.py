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
    def get_chat_list(user_id: int):
        return models.Chat.objects.filter(user_chats__user_id=user_id)

    @staticmethod
    def get_user_chats(user_id: int):
        last_messages = models.Message.objects.filter(chat=OuterRef('id')).order_by('-pk')
        chat_queryset = ChatService.get_chat_list(user_id)
        queryset = chat_queryset.annotate(
            last_message=Subquery(last_messages.values('content')[:1]),
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
        return response.data

    @staticmethod
    def get_chat_contacts(user_id: int):
        pass

    @staticmethod
    def get_chat_contacts_data(user_id: int, request):
        user_chats = models.Chat.objects.filter(user_chats__user_id=user_id)
        users_id: list[int] = list(
            models.UserChat.objects.exclude(
                user_id=user_id).filter(chat__in=user_chats).values_list('user_id', flat=True).distinct()
        )
        users_list: list[int] = []
        users_data: list[dict] = []
        for user in users_id:
            cache_key: str = cache.make_key('user', user)
            if cache_key not in cache:
                users_list.append(user)
            else:
                users_data.append(cache.get(cache_key))
        if users_list:
            response_data: list[dict] = ChatService.get_users_information(data=users_list, request=request)
            # TODO: UserData in response
            for user in response_data:
                cache_key = cache.make_key('user', user['id'])
                cache.set(cache_key, user, timeout=600)
                users_data.append(user)
        return users_data
