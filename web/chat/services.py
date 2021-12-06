from django.conf import settings
from django.db.models import OuterRef, Count, Subquery
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.cache import cache
from main.services import MainService
from . import models
from main.models import UserData

class ChatService:

    @staticmethod
    def add_users_to_chat(users: list, chat):
        objs = (models.UserChat(user_id=user, chat=chat) for user in users)
        models.UserChat.objects.bulk_create(objs)

    @staticmethod
    def get_user_chats(user_id: int):
        last_messages = models.Message.objects.filter(chat=OuterRef('id')).order_by('-pk')
        queryset = models.Chat.objects.filter(user_chats__user_id=user_id).annotate(
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
        response = service.service_response(method="post", data=data)
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
        # TODO: UserData in response
        user_data: list[dict] = ChatService.get_users_information(data=users_id, request=request)
        for user in user_data:
            cache_key = cache.make_key(user['id'], user)
            if not cache.get(cache_key):
                cache.set(cache_key, user, timeout=600)
        return user_data
